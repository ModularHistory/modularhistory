import BooleanField from "@/components/cms/fields/BooleanField";
import CharField from "@/components/cms/fields/CharField";
import HTMLField from "@/components/cms/fields/HTMLField";
import IntegerField from "@/components/cms/fields/IntegerField";

export const fieldComponents = {
  ManyToManyRel: undefined,
  ManyToOneRel: undefined,
  OneToOneRel: undefined,
  AutoField: undefined,
  AutoSlugField: CharField,
  HistoricDateTimeField: undefined,
  BooleanField: BooleanField,
  HTMLField: HTMLField,
  CharField: CharField,
  PostitiveSmallIntegerField: IntegerField,
  SourcesField: undefined,
  ImagesField: undefined,
  LocationsField: undefined,
  RelatedQuotesField: undefined,
  GenericRelation: undefined,
};
