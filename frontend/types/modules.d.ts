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
  title?: string;
  name?: string;
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

export interface Text {
  text?: string[]; // for quotes.quote
  description?: string[]; // for sources.source, entities.person
}
export interface Meta {
  score: number;
  highlight: Text;
  sort: number[];
}

export interface Quote extends SearchableModule, ModuleWithImages {
  model: "quotes.quote";
  title: string;
  attributeeHtml: string;
  attributeeString: string;
  bite: string;
  dateString: string;
  html: string;
  meta?: Meta;
  cachedCitations: Citation[];
}

export interface Occurrence extends SearchableModule, ModuleWithImages {
  model: "propositions.occurrence";
  title: string;
  dateString: string;
  elaboration: string;
  postscript: string;
  cachedCitations: Citation[];
  meta?: Meta; //Meta object
  summary: string;
}

export interface Source extends SearchableModule {
  model: "sources.source";
  title: string;
  citationHtml: string;
  citationString: string;
  meta?: Meta; //Meta object
  description: string;
}

export interface Entity extends BaseModule, SearchableModule, ModuleWithImages {
  model: "entities.entity" | "entities.organization" | "entities.person" | "entities.group";
  name: string;
  description: string;
  meta?: Meta; //Meta object
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
  meta?: Meta; //Meta object
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
