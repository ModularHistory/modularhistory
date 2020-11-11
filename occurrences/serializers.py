"""Serializers for the occurrences app."""

# TODO: https://medium.com/better-programming/how-to-use-drf-serializers-effectively-dc58edc73998
# TODO: https://www.valentinog.com/blog/drf/
# https://github.com/clarkduvall/serpy

import serpy

from modularhistory.models.searchable_model import SearchableModelSerializer


class OccurrenceSerializer(SearchableModelSerializer):
    """Serializer for occurrences."""

    date_html = serpy.Field()
    summary = serpy.MethodField()
    description = serpy.MethodField()
    postscript = serpy.MethodField()
    serialized_images = serpy.Field()
    serialized_citations = serpy.Field()
    tags_html = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'occurrences.occurrence'

    def get_summary(self, instance):
        """Return the user-facing summary HTML."""
        return instance.summary.html

    def get_description(self, instance):
        """Return the user-facing description HTML."""
        html = instance.description.html
        return html

    def get_postscript(self, instance):
        """Return the user-facing postscript HTML."""
        return instance.postscript.html if instance.postscript else ''
