import factory
from factory.django import DjangoModelFactory

from apps.users import models


class UserFactory(DjangoModelFactory):
    class Meta:
        model = models.User

    first_name = factory.Sequence(lambda n: 'Agent %03d' % n)
    # group = factory.SubFactory(GroupFactory)
