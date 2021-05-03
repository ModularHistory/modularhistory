export interface BaseModule {
  model: string;
  pk: number;
  slug: string;
  absoluteUrl: string;
  adminUrl: string;
}

export interface SearchableModule extends BaseModule {
  tagsHtml: string;
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
  description: string;
  bgImgPosition: string;
}

export interface ModuleWithImages {
  primaryImage: ImageModule;
  serializedImages: ImageModule[];
}

export interface QuoteModule extends SearchableModule, ModuleWithImages {
  attributeeHtml: string;
  bite: string;
  dateHtml: string;
  html: string;
  serializedCitations: Citation[];
}

export interface OccurrenceModule extends SearchableModule, ModuleWithImages {
  dateHtml: string;
  description: string;
  postscript: string;
  serializedCitations: Citation[];
  summary: string;
}

export interface SourceModule extends SearchableModule {
  citationHtml: string;
  citationString: string;
  description: string;
}

export interface EntityModule extends ModuleWithImages {
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
