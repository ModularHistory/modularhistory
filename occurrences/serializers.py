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

    def get_summary(self, instance):
        return instance.summary.html

    def get_description(self, instance):
        html = instance.description.html
        if '<<' in html:
            raise Exception('wth')
        return instance.description.html

    def get_postscript(self, instance):
        return instance.postscript.html if instance.postscript else ''
