import { Entity, Image, ModuleUnion, Occurrence, Proposition, Quote, Source } from "@/interfaces";
import { FC } from "react";
import HTMLEllipsis from "react-lines-ellipsis/lib/html";
import ModuleCard from "./ModuleCard";

interface ModuleUnionCardProps {
  module: ModuleUnion;
  selected?: boolean;
}

const ModuleUnionCard: FC<ModuleUnionCardProps> = ({
  module,
  selected,
  ...childProps
}: ModuleUnionCardProps) => {
  // ModuleUnionCard is a generic component for rendering cards of any
  // model type, removing the need to import every card component.
  let content;
  switch (module.model) {
    case "images.image":
      // return <ImageCard image={module} {...childProps} />;
      content = (
        <HTMLEllipsis unsafeHTML={(module as Image).captionHtml} maxLine="3" basedOn="words" />
      );
      break;
    case "propositions.occurrence":
      content = <div dangerouslySetInnerHTML={{ __html: (module as Occurrence).title }} />;
      break;
    case "propositions.proposition":
      content = <div dangerouslySetInnerHTML={{ __html: (module as Proposition).title }} />;
      break;
    case "quotes.quote": {
      const quote: Quote = module as Quote;
      content = (
        <blockquote className="blockquote">
          <HTMLEllipsis unsafeHTML={quote.bite} maxLine="4" basedOn="words" />
          {quote.attributeeString && (
            <footer
              className="blockquote-footer"
              dangerouslySetInnerHTML={{ __html: quote.attributeeString }}
            />
          )}
        </blockquote>
      );
      break;
    }
    case "sources.source":
      content = <div dangerouslySetInnerHTML={{ __html: (module as Source).citationHtml }} />;
      break;
    case "entities.person":
    case "entities.organization":
      content = <div dangerouslySetInnerHTML={{ __html: (module as Entity).name }} />;
      break;
  }
  return (
    <ModuleCard module={module} className={selected ? "selected" : ""} {...childProps}>
      {content}
    </ModuleCard>
  );
};

export default ModuleUnionCard;
