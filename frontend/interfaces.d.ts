export interface BaseModule {
  model: string;
  pk: number;
  slug: string;
  absoluteUrl: string;
  adminUrl: string;
  cachedImages?: ImageModule[];
  verified?: boolean;
  dateString?: string;
}

export interface SearchableModule extends BaseModule {
  tagsHtml: string;
  verified: boolean;
}

export interface Citation {
  pk: string;
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
  cachedImages: ImageModule[];
}

export interface QuoteModule extends SearchableModule, ModuleWithImages {
  title: string;
  attributeeHtml: string;
  bite: string;
  dateString: string;
  html: string;
  cachedCitations: Citation[];
}

export interface OccurrenceModule extends SearchableModule, ModuleWithImages {
  title: string;
  dateString: string;
  elaboration: string;
  postscript: string;
  cachedCitations: Citation[];
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

export interface PropositionModule extends BaseModule {
  summary: string;
  elaboration: string;
  certainty: string;
}

export interface TopicModule extends BaseModule {
  name: string;
  description: string;
}

export type ModuleUnion =
  | ImageModule
  | QuoteModule
  | OccurrenceModule
  | SourceModule
  | EntityModule
  | PropositionModule
  | TopicModule;

export interface StaticPage {
  title: string;
  content: string;
}
