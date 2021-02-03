"""HistoricDateTime module."""

# TODO: optimize memory by storing attributes in __init__?

from datetime import datetime
from decimal import Decimal, getcontext
from typing import Optional

import sigfig
from django.utils.html import format_html
from django.utils.safestring import SafeString
from millify import millify, prettify

SEASONS = (
    (None, '-----'),
    ('winter', 'Winter'),
    ('spring', 'Spring'),
    ('summer', 'Summer'),
    ('fall', 'Fall'),
)

TEN_THOUSAND = 10000
ONE_MILLION = 1000000

SIGNIFICANT_FIGURES = 4

APPROXIMATE_PRESENT_YEAR = 2000

# https://en.wikipedia.org/wiki/Before_Present
BP_REFERENCE_YEAR = 1950

YBP_LOWER_LIMIT = 29999  # 30000 with rounding error protection

BCE_THRESHOLD = YBP_LOWER_LIMIT - BP_REFERENCE_YEAR

# Dates earlier than this are considered to be circa by default
BCE_CIRCA_FLOOR = TEN_THOUSAND

# Dates earlier than this are considered to be prehistory
BCE_PREHISTORY_FLOOR = TEN_THOUSAND

# Year values larger than this should be expressed in millions/billions
MILLIFICATION_FLOOR = ONE_MILLION

# Year values larger than this should be "prettified" with commas
PRETTIFICATION_FLOOR = TEN_THOUSAND

EXPONENT_INVERSION_BASIS = 30  # --> 20 for the Big Bang
DECIMAL_INVERSION_BASIS = 100000  # --> 986200 for the Big Bang


def get_season_from_month(month: int) -> str:
    """Infer season from month."""
    if month in {1, 2, 3}:
        return SEASONS[1][0]
    elif month in {4, 5, 6}:
        return SEASONS[2][0]
    elif month in {7, 8, 9}:
        return SEASONS[3][0]
    return SEASONS[4][0]


def get_month_from_season(season: str) -> int:
    """Infer approximate month from season."""
    if season == SEASONS[1][0]:
        return 1
    elif season == SEASONS[2][0]:
        return 4
    elif season == SEASONS[3][0]:
        return 7
    return 10


class HistoricDateTime(datetime):
    """Datetime capable of representing dates before CE."""

    ybp_lower_limit = YBP_LOWER_LIMIT
    bce_threshold = YBP_LOWER_LIMIT - BP_REFERENCE_YEAR
    significant_figures = SIGNIFICANT_FIGURES

    def __str__(self) -> str:
        """Return the datetime's string representation."""
        return self.string

    def serialize(self) -> str:
        """Serialize the datetime to a JSON-compatible string value."""
        return self.isoformat()

    @property
    def html(self) -> SafeString:
        """Return the datetime's HTML representation."""
        return format_html(f'<span class="date">{self.string}</span>')

    @property
    def is_bce(self) -> bool:
        """Whether the date is before common era (BCE)."""
        # Python can only create date objects with year >= 1.
        # All historic dates BCE are set with a year value of 1 in the db.
        # The year BCE is calculated from the object's second and microsecond values.
        return bool(self.year <= 1 and self.microsecond)

    @property
    def is_circa(self) -> bool:
        """
        Return True if the datetime is circa, i.e., approximate.

        Circa dates should be displayed with a "c." preface.
        """
        return self.is_bce and self.year_bce >= BCE_CIRCA_FLOOR

    @property
    def season_is_known(self) -> bool:
        """Return True if the datetime precision is high enough for its season to be displayed."""
        return self.hour != 1

    @property
    def month_is_known(self) -> bool:
        """Return True if the datetime precision is high enough for its month to be displayed."""
        return self.minute != 1

    @property
    def day_is_known(self) -> bool:
        """Return True if the datetime precision is high enough for its day to be displayed."""
        return not self.second

    @property
    def use_ybp(self) -> bool:
        """Return True if the datetime should be displayed using the YBP system."""
        return self.is_bce and self.year_bce > self.bce_threshold

    @property
    def year_bce(self) -> Optional[int]:
        """BCE."""
        if self.is_bce and self.microsecond:
            getcontext().prec = self.significant_figures
            inv_exponent = self.second
            inv_decimal_num = self.microsecond
            exponent = -(inv_exponent - EXPONENT_INVERSION_BASIS)
            decimal_num = Decimal(
                ('{:.4e}'.format(-(inv_decimal_num - DECIMAL_INVERSION_BASIS))).split(
                    'e+'
                )[0]
            )
            multiplier = Decimal(10 ** exponent)
            bce = int(Decimal(decimal_num * multiplier))
            if bce > BCE_PREHISTORY_FLOOR:  # if prehistory
                bce = round(bce / 100) * 100
            return int(bce)
        return None

    @property
    def year_bp(self) -> int:
        """Return the year in YBP (years before present)."""
        current_year = datetime.now().year
        if self.is_bce:
            ybp = self.year_bce + APPROXIMATE_PRESENT_YEAR
        else:
            ybp = current_year - self.year
        ybp = int(sigfig.round(ybp, sigfigs=self.significant_figures))
        # Correct rounding error if needed
        if TEN_THOUSAND < ybp < ONE_MILLION:  # TODO: use BCE if smaller than this
            scale = 500
            ybp = round(ybp / scale) * scale
        return int(ybp)

    @property
    def season(self) -> Optional[str]:
        """Return the season of the datetime, if the season is known."""
        return str(get_season_from_month(self.month)) if self.season_is_known else None

    @property
    def second(self) -> int:
        """
        Return the datetime's "second" value.

        NOTE: This value is not used to reflect the actual second.  Instead, it is:
          * 1 if the date's day is unknown, or
          * A value 1–9 representing the inverse of the 10-based exponent used to
            calculate a year BCE; see the year_bce property
        """
        return super().second

    @property
    def string(self) -> str:
        """Return the datetime's string representation."""
        year_string = self.year_string
        if self.day_is_known:
            year_string = f'{self.strftime("%-d %b")} {year_string}'
        elif self.month_is_known:
            year_string = f'{self.strftime("%B")} {year_string}'
        elif self.season_is_known and self.season:
            year_string = f'{self.season.title()} {year_string}'
        return year_string

    @property
    def year_string(self) -> str:
        """Return a string representation of the datetime's year."""
        if self.is_bce:
            if self.use_ybp:
                # YBP dates
                ybp, humanized_ybp = self.year_bp, None
                if ybp >= MILLIFICATION_FLOOR:
                    humanized_ybp = millify(ybp, precision=self.significant_figures)
                elif ybp >= PRETTIFICATION_FLOOR:
                    humanized_ybp = prettify(ybp)
                else:
                    humanized_ybp = ybp
                year_string = f'c. {humanized_ybp} YBP'
            else:
                # BCE dates
                prettify_circa_year = (
                    self.year_bce >= PRETTIFICATION_FLOOR
                    and self.year_bce >= BCE_CIRCA_FLOOR
                )
                if prettify_circa_year:
                    year_string = f'c. {prettify(self.year_bce)}'
                elif self.year_bce >= PRETTIFICATION_FLOOR:
                    year_string = f'{prettify(self.year_bce)}'
                else:
                    year_string = f'{self.year_bce}'
                year_string = f'{year_string} BCE'
        else:
            # CE dates
            year_string = str(self.year)
        return year_string
