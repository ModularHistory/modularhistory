from datetime import datetime
from typing import Optional

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
    def __str__(self):
        return self.string

    @property
    def season_is_known(self) -> bool:
        return self.hour != 1

    @property
    def month_is_known(self) -> bool:
        return self.minute != 1

    @property
    def day_is_known(self) -> bool:
        return self.second != 1

    @property
    def season(self) -> Optional[str]:
        return str(get_season_from_month(self.month)) if self.season_is_known else None

    @property
    def string(self) -> str:
        if self.day_is_known:
            return self.strftime('%-d %b %Y')
        elif self.month_is_known:
            return self.strftime('%B %Y')
        elif self.season_is_known:
            return f'{self.season.title()} {self.year}'
        else:
            return str(self.year)
