from factory.django import DjangoModelFactory


class ModeratedModelFactory(DjangoModelFactory):
    verified = True

    @classmethod
    def create(cls, **kwargs):
        kwargs.setdefault('verified', True)
        return super(DjangoModelFactory, cls).create(**kwargs)
