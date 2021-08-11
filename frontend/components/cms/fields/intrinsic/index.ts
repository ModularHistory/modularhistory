import BooleanField from "@/components/cms/fields/intrinsic/BooleanField";
import CharField from "@/components/cms/fields/intrinsic/CharField";
import HTMLField from "@/components/cms/fields/intrinsic/HTMLField";
import IntegerField from "@/components/cms/fields/intrinsic/IntegerField";

export const intrinsicFieldComponents = {
  AutoField: undefined,
  AutoSlugField: CharField,
  HistoricDateTimeField: undefined,
  BooleanField: BooleanField,
  HTMLField: HTMLField,
  CharField: CharField,
  PostitiveSmallIntegerField: IntegerField,
};
