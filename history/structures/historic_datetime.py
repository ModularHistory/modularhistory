from datetime import datetime
from decimal import Decimal, getcontext
from typing import Optional

from django.utils.safestring import SafeText, mark_safe
import sigfig
from millify import prettify, millify

seasons = (
    (None, '-----'),
    ('winter', 'Winter'),
    ('spring', 'Spring'),
    ('summer', 'Summer'),
    ('fall', 'Fall')
)


def get_season_from_month(month: int) -> str:
    return (seasons[1][0] if month in (1, 2, 3) else
            seasons[2][0] if month in (4, 5, 6) else
            seasons[3][0] if month in (7, 8, 9) else
            seasons[4][0])


def get_month_from_season(season: str) -> int:
    return (1 if season == seasons[1][0] else
            4 if season == seasons[2][0] else
            7 if season == seasons[3][0] else
            10)


class HistoricDateTime(datetime):
    ybp_lower_limit = 29999  # 30000 with rounding error protection
    bce_threshold = ybp_lower_limit - 1950
    significant_figures = 4

    def __str__(self):
        return self.string

    @property
    def html(self) -> SafeText:
        """Whether the date is before common era (BCE)."""
        return mark_safe(f'<span style="display: inline-block; white-space: nowrap;">{self.string}</span>')

    @property
    def is_bce(self) -> bool:
        """Whether the date is before common era (BCE)."""
        # Python can only create date objects with year >= 1.
        # All historic dates BCE are set with a year value of 1 in the db.
        # The year BCE is calculated from the object's second and microsecond values.
        return self.year <= 1 and self.microsecond

    @property
    def is_circa(self) -> bool:
        return True if (self.is_bce and self.year_bce <= 9999) else False

    @property
    def season_is_known(self) -> bool:
        return self.hour != 1

    @property
    def month_is_known(self) -> bool:
        return self.minute != 1

    @property
    def day_is_known(self) -> bool:
        return not self.second

    @property
    def use_ybp(self) -> bool:
        return self.is_bce and self.year_bce > self.bce_threshold

    @property
    def year_bce(self) -> Optional[int]:
        """BCE"""
        if self.is_bce and self.microsecond:
            getcontext().prec = self.significant_figures
            inv_exponent = self.second
            inv_decimal_num = self.microsecond
            exponent = -(inv_exponent - 30)
            decimal_num = '{:.4e}'.format(-(inv_decimal_num - 100000))
            decimal_num = Decimal(decimal_num.split('e+')[0])
            multiplier = Decimal(10**exponent)
            bce = int(Decimal(decimal_num * multiplier))
            if bce > 10000:  # if prehistory
                bce = round(bce / 100) * 100
            return int(bce)
        return None

    @property
    def year_bp(self) -> int:
        """YBP"""
        getcontext().prec = self.significant_figures
        current_year = datetime.now().year
        if self.is_bce:
            ybp = Decimal(self.year_bce + 2000)
        else:
            ybp = Decimal(current_year - self.year)
        ybp = int(sigfig.round(ybp, sigfigs=self.significant_figures))
        # Correct rounding error if needed
        if 1000000 > ybp > 10000:  # Should use BCE is smaller than this
            scale = 500
            ybp = round(ybp / scale) * scale
        return int(ybp)

    @property
    def season(self) -> Optional[str]:
        return str(get_season_from_month(self.month)) if self.season_is_known else None

    @property
    def second(self) -> int:
        """
        Second is set to:
          * 1 if the date's day is unknown, or
          * A value 1–9 representing the inverse of the 10-based exponent used to calculate a year BCE;
            see the year_bce property
        """
        return super().second

    @property
    def string(self) -> SafeText:
        year_string = self.year_string
        if self.day_is_known:
            year_string = f'{self.strftime("%-d %b")} {year_string}'
        elif self.month_is_known:
            year_string = f'{self.strftime("%B")} {year_string}'
        elif self.season_is_known:
            year_string = f'{self.season.title()} {year_string}'
        return mark_safe(year_string)

    @property
    def year_string(self) -> str:
        if not self.is_bce:
            # CE dates
            year_string = str(self.year)
        elif not self.use_ybp:
            # BCE dates
            year_string = f'{self.year_bce if self.year_bce <= 9999 else "c. " + prettify(self.year_bce)} BCE'
        else:
            # YBP dates
            ybp, humanized_ybp = self.year_bp, None
            if ybp > 999999:
                humanized_ybp = millify(ybp, precision=self.significant_figures)
            elif ybp > 9999:
                humanized_ybp = prettify(ybp)
            else:
                humanized_ybp = ybp
            year_string = f'c. {humanized_ybp} YBP'
        return year_string
