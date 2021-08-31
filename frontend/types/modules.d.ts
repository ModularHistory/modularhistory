import { User } from "next-auth";

export interface BaseModule {
  model: string;
  id: number;
  slug: string;
  absoluteUrl: string;
  adminUrl: string;
  cachedImages?: Image[];
  verified?: boolean;
  dateString?: string;
  changes?: Change[];
  issues?: Issue[];
}

export interface SearchableModule extends BaseModule {
  title: string;
  cachedTags: Topic[];
  verified: boolean;
}

export interface Citation {
  id: number;
  html: string;
}

export interface Image extends SearchableModule {
  model: "images.image";
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
  model: "quotes.quote";
  title: string;
  attributeeHtml: string;
  attributeeString: string;
  bite: string;
  dateString: string;
  html: string;
  cachedCitations: Citation[];
}

export interface Occurrence extends SearchableModule, ModuleWithImages {
  model: "propositions.occurrence";
  title: string;
  dateString: string;
  elaboration: string;
  postscript: string;
  cachedCitations: Citation[];
  summary: string;
}

export interface Source extends SearchableModule {
  model: "sources.source";
  title: string;
  citationHtml: string;
  citationString: string;
  description: string;
}

export interface Entity extends BaseModule, SearchableModule, ModuleWithImages {
  model: "entities.entity" | "entities.organization" | "entities.person";
  name: string;
  description: string;
}

export interface Argument extends BaseModule {
  type: string;
  explanation: string;
  premises: Proposition[];
}

export interface Proposition extends BaseModule {
  model: "propositions.proposition";
  title: string;
  summary: string;
  elaboration: string;
  certainty: number;
  arguments: Argument[];
  conflictingPropositions: Proposition[];
}

export interface Topic extends BaseModule {
  model: "topics.topic";
  name: string;
  title: string;
  description: string;
  propositions: Proposition[];
}

export type ModuleUnion = Image | Quote | Occurrence | Source | Entity | Proposition | Topic;

export interface FlatPage {
  title: string;
  content: string;
}

export interface Change {
  id: number;
  url: string;
  initiator: User;
  description: string;
  changedObject?: ModuleUnion;
  unchangedObject?: ModuleUnion;
}

export interface Issue {
  id: number;
  url: string;
  title: string;
}
