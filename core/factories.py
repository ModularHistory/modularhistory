from typing import TYPE_CHECKING

import factory

if TYPE_CHECKING:
    from faker import Faker
    from faker.proxy import UniqueProxy


class UniqueFaker(factory.Faker):
    def generate(self, params):
        print(f'>>>>>> {params=}')
        locale = params.pop('locale')
        subfaker: 'Faker' = self._get_faker(locale)
        unique_proxy: 'UniqueProxy' = subfaker.unique  # has access to attributes of Faker
        ret = unique_proxy.format(self.provider, **params)
        print(f'>>>>>> {ret=}')
        return unique_proxy.format(self.provider, **params)
