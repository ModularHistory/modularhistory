import factory
from factory.django import DjangoModelFactory

from apps.users import models


class UserFactory(DjangoModelFactory):
    class Meta:
        model = models.User

    first_name = factory.Sequence(lambda n: 'User %03d' % n)
    username = factory.Sequence(lambda n: 'user%03d' % n)
    email = factory.Sequence(lambda n: 'user%03d@gmail.com' % n)
    # group = factory.SubFactory(GroupFactory)
