from factory.django import DjangoModelFactory


class ModeratedModelFactory(DjangoModelFactory):
    verified = True
