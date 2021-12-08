from typing import TYPE_CHECKING

import factory

if TYPE_CHECKING:
    from faker import Faker
    from faker.proxy import UniqueProxy


class UniqueFaker(factory.Faker):
    def evaluate(self, instance, step, extra):
        locale = extra.pop('locale')
        subfaker: 'Faker' = self._get_faker(locale)
        unique_proxy: 'UniqueProxy' = subfaker.unique
        return unique_proxy.format(self.provider, **extra)
