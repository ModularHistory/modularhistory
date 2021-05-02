export interface BaseModule {
  model: string;
  pk: number;
  slug: string;
  absolute_url: string;
  admin_url: string;
}

export interface SearchableModule extends BaseModule {
  tags_html: string;
  verified: boolean;
}

export interface Citation {
  html: string;
}

export interface ImageModule extends SearchableModule {
  srcUrl: string;
  width: number;
  height: number;
  captionHtml: string;
  providerString: string;
  bgImgPosition: string;
}

export interface ModuleWithImages {
  primary_image: ImageModule;
  serialized_images: ImageModule[];
}

export interface QuoteModule extends SearchableModule, ModuleWithImages {
  attributee_html: string;
  bite: string;
  date_html: string;
  has_multiple_attributees: boolean;
  html: string;
  serialized_citations: Citation[];
  truncated_html: string;
}

export interface OccurrenceModule extends SearchableModule, ModuleWithImages {
  date_html: string;
  description: string;
  postscript: string;
  serialized_citations: Citation[];
  summary: string;
}

export interface SourceModule extends SearchableModule {
  citationHtml: string;
  citationString: string;
  description: string;
}

export interface EntityModule extends ModuleWithImages {
  serialized_citations: Citation[];
  description: string;
}

export interface PostulationModule extends BaseModule {
  summary: string;
  elaboration: string;
  certainty: string;
}

export interface TopicModule extends BaseModule {
  description: string;
}

export interface StaticPage {
  title: string;
  content: string;
}
