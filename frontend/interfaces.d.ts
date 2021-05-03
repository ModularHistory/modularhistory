export interface BaseModule {
  model: string;
  pk: number;
  slug: string;
  absoluteUrl: string;
  adminUrl: string;
  serializedImages?: Array<ImageModule>;
  verified?: boolean;
  dateHtml?: string;
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
  title: string;
  attributeeHtml: string;
  bite: string;
  dateHtml: string;
  html: string;
  serializedCitations: Citation[];
}

export interface OccurrenceModule extends SearchableModule, ModuleWithImages {
  title: string;
  dateHtml: string;
  description: string;
  postscript: string;
  serializedCitations: Citation[];
  summary: string;
}

export interface SourceModule extends SearchableModule {
  title: string;
  citationHtml: string;
  citationString: string;
  description: string;
}

export interface EntityModule extends BaseModule, ModuleWithImages {
  name: string;
  description: string;
}

export interface PostulationModule extends BaseModule {
  summary: string;
  elaboration: string;
  certainty: string;
}

export interface TopicModule extends BaseModule {
  name: string;
  description: string;
}

export interface StaticPage {
  title: string;
  content: string;
}
