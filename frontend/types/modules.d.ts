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
  title?: string;
  name?: string;
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
  meta?: Meta;
}

export interface ModuleWithImages {
  primaryImage: Image;
  cachedImages: Image[];
}

export interface Text {
  text?: string[]; // for quotes.quote
  description?: string[]; // for sources.source, entities.person
  elaboration?: string[]; // for occurances
}
export interface Meta {
  score: number;
  highlight: Text;
  sort: number[];
}

export interface Quote extends SearchableModule, ModuleWithImages {
  model: "quotes.quote";
  attributeeHtml: string;
  attributeeString: string;
  bite: string;
  dateString: string;
  html: string;
  meta?: Meta;
  cachedCitations: Citation[];
}

export interface Occurrence extends Proposition {
  model: "propositions.occurrence";
}

export interface Source extends SearchableModule {
  model: "sources.source";
  citationHtml: string;
  citationString: string;
  meta?: Meta;
  description: string;
}

export interface Entity extends SearchableModule, ModuleWithImages {
  model: "entities.entity" | "entities.organization" | "entities.person" | "entities.group";
  name: string;
  description: string;
  truncatedDescription: string;
  meta?: Meta;
  relatedQuotes?: Quote[];
}

export interface Argument extends BaseModule {
  type: string;
  explanation: string;
  premises: Proposition[];
}

export interface Proposition extends SearchableModule, ModuleWithImages {
  model: "propositions.proposition";
  summary: string;
  elaboration: string;
  truncatedElaboration: string;
  certainty: number;
  arguments: Argument[];
  meta?: Meta;
  conflictingPropositions: Proposition[];
  dateString: string;
  postscript: string;
  cachedCitations: Citation[];
}

export interface Topic extends BaseModule {
  model: "topics.topic";
  name: string;
  description: string;
  meta?: Meta;
  propositions: Proposition[];
}

export type ModuleUnion = Image | Quote | Occurrence | Source | Entity | Proposition | Topic;

export interface FlatPage {
  title: string;
  content: string;
  path: string;
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
