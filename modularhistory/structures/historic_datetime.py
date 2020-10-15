from datetime import datetime
from decimal import Decimal, getcontext
from typing import Optional

from django.utils.safestring import SafeString
from django.utils.html import format_html
import sigfig
from millify import prettify, millify

SEASONS = (
    (None, '-----'),
    ('winter', 'Winter'),
    ('spring', 'Spring'),
    ('summer', 'Summer'),
    ('fall', 'Fall')
)

SIGNIFICANT_FIGURES = 4

APPROXIMATE_PRESENT_YEAR = 2000

MILLIFICATION_FLOOR = 999999

YBP_LOWER_LIMIT = 29999  # 30000 with rounding error protection

# Dates earlier than this are considered to be circa by default
BCE_CIRCA_FLOOR = 9999

# Dates earlier than this are considered to be prehistory
BCE_PREHISTORY_FLOOR = 10000


def get_season_from_month(month: int) -> str:
    """TODO: add docstring."""
    if month in {1, 2, 3}:
        return SEASONS[1][0]
    elif month in {4, 5, 6}:
        return SEASONS[2][0]
    elif month in {7, 8, 9}:
        return SEASONS[3][0]
    return SEASONS[4][0]


def get_month_from_season(season: str) -> int:
    """TODO: add docstring."""
    if season == SEASONS[1][0]:
        return 1
    elif season == SEASONS[2][0]:
        return 4
    elif season == SEASONS[3][0]:
        return 7
    return 10


class HistoricDateTime(datetime):
    """TODO: add docstring."""

    ybp_lower_limit = YBP_LOWER_LIMIT
    bce_threshold = ybp_lower_limit - 1950
    significant_figures = SIGNIFICANT_FIGURES

    def __str__(self) -> str:
        """TODO: write docstring."""
        return self.string

    @property
    def html(self) -> SafeString:
        """TODO: write docstring."""
        return format_html(f'<span style="display: inline-block; white-space: nowrap;">{self.string}</span>')

    @property
    def is_bce(self) -> bool:
        """Whether the date is before common era (BCE)."""
        # Python can only create date objects with year >= 1.
        # All historic dates BCE are set with a year value of 1 in the db.
        # The year BCE is calculated from the obj's second and microsecond values.
        return bool(self.year <= 1 and self.microsecond)

    @property
    def is_circa(self) -> bool:
        """TODO: write docstring."""
        return self.is_bce and self.year_bce > BCE_CIRCA_FLOOR

    @property
    def season_is_known(self) -> bool:
        """TODO: write docstring."""
        return self.hour != 1

    @property
    def month_is_known(self) -> bool:
        """TODO: write docstring."""
        return self.minute != 1

    @property
    def day_is_known(self) -> bool:
        """TODO: write docstring."""
        return not self.second

    @property
    def use_ybp(self) -> bool:
        """TODO: write docstring."""
        return self.is_bce and self.year_bce > self.bce_threshold

    @property
    def year_bce(self) -> Optional[int]:
        """BCE."""
        if self.is_bce and self.microsecond:
            getcontext().prec = self.significant_figures
            inv_exponent = self.second
            inv_decimal_num = self.microsecond
            exponent = -(inv_exponent - 30)
            decimal_num = Decimal(('{:.4e}'.format(-(inv_decimal_num - 100000))).split('e+')[0])
            multiplier = Decimal(10**exponent)
            bce = int(Decimal(decimal_num * multiplier))
            if bce > BCE_PREHISTORY_FLOOR:  # if prehistory
                bce = round(bce / 100) * 100
            return int(bce)
        return None

    @property
    def year_bp(self) -> int:
        """The year expressed in YBP (years before present)."""
        # TODO: test cutting out the Decimal nonsense and just using sigfig
        getcontext().prec = self.significant_figures
        current_year = datetime.now().year
        if self.is_bce:
            _ybp = Decimal(self.year_bce + APPROXIMATE_PRESENT_YEAR)
        else:
            _ybp = Decimal(current_year - self.year)
        ybp = int(sigfig.round(_ybp, sigfigs=self.significant_figures))
        # Correct rounding error if needed
        if 10000 < ybp < 1000000:  # Should use BCE is smaller than this
            scale = 500
            ybp = round(ybp / scale) * scale
        return int(ybp)

    @property
    def season(self) -> Optional[str]:
        """TODO: write docstring."""
        return str(get_season_from_month(self.month)) if self.season_is_known else None

    @property
    def second(self) -> int:
        """
        This value IS NOT USED to reflect the actual second at which something happened.

        It is set to:
          * 1 if the date's day is unknown, or
          * A value 1–9 representing the inverse of the 10-based exponent used to calculate a year BCE;
            see the year_bce property
        """
        return super().second

    @property
    def string(self) -> SafeString:
        """TODO: write docstring."""
        year_string = self.year_string
        if self.day_is_known:
            year_string = f'{self.strftime("%-d %b")} {year_string}'
        elif self.month_is_known:
            year_string = f'{self.strftime("%B")} {year_string}'
        elif self.season_is_known:
            year_string = f'{self.season.title()} {year_string}'
        return format_html(year_string)

    @property
    def year_string(self) -> str:
        """TODO: write docstring."""
        if self.is_bce:
            if self.use_ybp:
                # YBP dates
                ybp, humanized_ybp = self.year_bp, None
                if ybp > MILLIFICATION_FLOOR:
                    humanized_ybp = millify(ybp, precision=self.significant_figures)
                elif ybp > 9999:
                    humanized_ybp = prettify(ybp)
                else:
                    humanized_ybp = ybp
                year_string = f'c. {humanized_ybp} YBP'
            else:
                # BCE dates
                if self.year_bce <= 9999:
                    year_string = f'{self.year_bce}'
                else:
                    year_string = f'c. {prettify(self.year_bce)}'
                year_string = f'{year_string} BCE'
        else:
            # CE dates
            year_string = str(self.year)
        return year_string
