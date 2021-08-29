import { ModuleUnion, Topic } from "@/types/modules";
import { FC } from "react";
import HTMLEllipsis from "react-lines-ellipsis/lib/html";
import ModuleCard from "./ModuleCard";

interface ModuleUnionCardProps {
  module: Exclude<ModuleUnion, Topic>;
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
      content = <HTMLEllipsis unsafeHTML={module.captionHtml} maxLine="3" basedOn="words" />;
      break;
    case "propositions.occurrence":
      content = <div dangerouslySetInnerHTML={{ __html: module.title }} />;
      break;
    case "propositions.proposition":
      content = <div dangerouslySetInnerHTML={{ __html: module.title }} />;
      break;
    case "quotes.quote": {
      content = (
        <blockquote className="blockquote">
          <HTMLEllipsis unsafeHTML={module.bite} maxLine="4" basedOn="words" />
          {module.attributeeString && (
            <footer
              className="blockquote-footer"
              dangerouslySetInnerHTML={{ __html: module.attributeeString }}
            />
          )}
        </blockquote>
      );
      break;
    }
    case "sources.source":
      content = <div dangerouslySetInnerHTML={{ __html: module.citationHtml }} />;
      break;
    case "entities.person":
    case "entities.organization":
    case "entities.entity":
      content = <div dangerouslySetInnerHTML={{ __html: module.name }} />;
      break;
    default:
      ((module: never) => {
        throw new Error(`Unexpected module type encountered: ${(module as any).model}`);
      })(module);
  }
  return (
    <ModuleCard module={module} className={selected ? "selected" : ""} {...childProps}>
      {content}
    </ModuleCard>
  );
};

export default ModuleUnionCard;
