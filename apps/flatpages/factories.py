import factory
from django.conf import settings
from django.contrib.sites.models import Site
from factory.django import DjangoModelFactory

from apps.flatpages import models
from apps.moderation.factories import ModeratedModelFactory


class SiteFactory(DjangoModelFactory):
    class Meta:
        model = Site


class FlatPageFactory(ModeratedModelFactory):
    class Meta:
        model = models.FlatPage

    path = factory.Sequence(lambda n: f'/original/path/{n}')
    title = factory.Sequence(lambda n: f'Page {n}')

    @factory.post_generation
    def sites(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            # A list of groups were passed in, use them
            for site in extracted:
                self.sites.add(site)
        else:
            self.sites.add(Site.objects.get(pk=settings.SITE_ID))
