export interface BaseModule {
  model: string;
  pk: number;
  slug: string;
  absoluteUrl: string;
  adminUrl: string;
  cachedImages?: Image[];
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

export interface Image extends SearchableModule {
  srcUrl: string;
  width: number;
  height: number;
  captionHtml: string;
  providerString: string;
  description: string;
  bgImgPosition: string;
}

export interface ModuleWithImages {
  primaryImage: Image;
  cachedImages: Image[];
}

export interface Quote extends SearchableModule, ModuleWithImages {
  title: string;
  attributeeHtml: string;
  attributeeString: string;
  bite: string;
  dateString: string;
  html: string;
  cachedCitations: Citation[];
}

export interface Occurrence extends SearchableModule, ModuleWithImages {
  title: string;
  dateString: string;
  elaboration: string;
  postscript: string;
  cachedCitations: Citation[];
  summary: string;
}

export interface Source extends SearchableModule {
  title: string;
  citationHtml: string;
  citationString: string;
  description: string;
}

export interface Entity extends BaseModule, ModuleWithImages {
  name: string;
  description: string;
}

export interface Argument extends BaseModule {
  type: string;
  explanation: string;
  premises: Proposition[];
}

export interface Proposition extends BaseModule {
  summary: string;
  elaboration: string;
  certainty: number;
  arguments: Argument[];
  conflictingPropositions: Proposition[];
}

export interface Topic extends BaseModule {
  name: string;
  description: string;
  propositions: Proposition[];
}

export type ModuleUnion = Image | Quote | Occurrence | Source | Entity | Proposition | Topic;

export interface StaticPage {
  title: string;
  content: string;
}
