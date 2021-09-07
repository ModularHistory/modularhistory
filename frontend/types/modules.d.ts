import { User } from "next-auth";

export interface BaseModule {
  model: string;
  id: number;
  slug: string;
  absoluteUrl: string;
  adminUrl: string;
  title: string;
  cachedImages?: Image[];
  verified?: boolean;
  dateString?: string;
  changes?: Change[];
  issues?: Issue[];
}

export interface SearchableModule extends BaseModule {
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
  attributeeHtml: string;
  attributeeString: string;
  bite: string;
  dateString: string;
  html: string;
  cachedCitations: Citation[];
}

export interface Occurrence extends Proposition, SearchableModule, ModuleWithImages {
  model: "propositions.occurrence";
}

export interface Source extends SearchableModule {
  model: "sources.source";
  citationHtml: string;
  citationString: string;
  description: string;
}

export interface Entity extends SearchableModule, ModuleWithImages {
  model: "entities.entity" | "entities.organization" | "entities.person" | "entities.group";
  name: string;
  description: string;
}

export interface Argument {
  type: string;
  explanation: string;
  premises: Proposition[];
}

export interface Proposition extends SearchableModule {
  model: "propositions.proposition";
  summary: string;
  elaboration: string;
  certainty: number;
  arguments: Argument[];
  conflictingPropositions: Proposition[];
  dateString: string;
  postscript: string;
  cachedCitations: Citation[];
}

export interface Topic extends BaseModule {
  model: "topics.topic";
  name: string;
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
