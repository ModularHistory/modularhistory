export interface BaseModule {
  model: string;
  pk: number;
}

export interface SearchableModule extends BaseModule {
  absolute_url: string;
  admin_url: string;
  slug: string;
  tags_html: string;
  verified: boolean;
}

export interface Citation {
  html: string;
}

export interface ImageModule extends SearchableModule {
  src_url: string;
  width: number;
  height: number;
  caption_html: string;
  provider_string: string;
  bg_img_position: string;
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

export interface EntityModule extends ModuleWithImages {
  serialized_citations: Citation[];
  description: string;
}

export interface StaticPage {
  title: string;
  content: string;
}
