import ImagesField from "./ImagesField";
import LocationsField from "./LocationsField";
import ManyToOneField from "./ManyToOneField";
import SourcesField from "./SourcesField";
import TagsField from "./TagsField";

export const relatedFieldComponents = {
  ManyToManyRel: undefined,
  ManyToOneRel: ManyToOneField,
  OneToOneRel: undefined,
  SourcesField: SourcesField,
  ImagesField: ImagesField,
  TagsField: TagsField,
  LocationsField: LocationsField,
  RelatedQuotesField: undefined,
  GenericRelation: undefined,
};
