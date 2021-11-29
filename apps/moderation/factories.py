from factory.django import DjangoModelFactory


class ModeratedModelFactory(DjangoModelFactory):
    verified = True

    @classmethod
    def create(cls, **kwargs):
        kwargs.setdefault('verified', True)
        return super(DjangoModelFactory, cls).create(**kwargs)

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """Save again the instance if creating and at least one hook ran."""
        if create and results:
            # Some post-generation hooks ran, and may have modified us.
            instance.save(moderate=False)
