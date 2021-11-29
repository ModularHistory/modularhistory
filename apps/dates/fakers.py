import factory
from faker.providers import BaseProvider

from apps.dates.structures import HistoricDateTime


class HistoricDateTimeProvider(BaseProvider):
    def historic_datetime(self) -> HistoricDateTime:
        return HistoricDateTime.now()


factory.Faker.add_provider(HistoricDateTimeProvider)
