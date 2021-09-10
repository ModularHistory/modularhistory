import { ModuleUnion, Topic } from "@/types/modules";
import { Box } from "@material-ui/system";
import React, { FC } from "react";
import HTMLEllipsis from "react-lines-ellipsis/lib/html";
import ModuleCard from "./ModuleCard";

interface ModuleUnionCardProps {
  module: Exclude<ModuleUnion, Topic>;
  selected?: boolean;
}

interface HighlightEllipsisProps {
  unsafeHTML: string;
}

const HighlightEllipsis: FC<HighlightEllipsisProps> = ({ unsafeHTML }) => (
  <Box
    sx={{
      "& *": { fontSize: "0.8rem", backgroundColor: "rgba(0, 0, 0, 0)" },
      "& mark": { fontWeight: "500", color: "white" },
    }}
  >
    <HTMLEllipsis
      unsafeHTML={unsafeHTML.replace(/(<(h[1-6])>.*?<\/h[1-6]>)/gi, "")}
      maxLine="4"
      basedOn="words"
    />
  </Box>
);

const ModuleUnionCard: FC<ModuleUnionCardProps> = ({
  module,
  selected,
  ...childProps
}: ModuleUnionCardProps) => {
  // ModuleUnionCard is a generic component for rendering cards of any
  // model type, removing the need to import every card component.
  let content;
  const highlightSnippet =
    module?.meta?.highlight?.text?.[0] ?? module?.meta?.highlight?.description?.[0]; // highlight text or highlight description
  switch (module.model) {
    case "images.image":
      // return <ImageCard image={module} {...childProps} />;
      content = <HTMLEllipsis unsafeHTML={module.captionHtml} maxLine="3" basedOn="words" />;
      break;
    case "propositions.occurrence":
      content = highlightSnippet && ( // TODO: Replace Regex with more formal fix
        <HighlightEllipsis unsafeHTML={highlightSnippet} />
      );
      break;
    case "propositions.proposition":
      content = highlightSnippet && ( // TODO: Replace Regex with more formal fix
        <HighlightEllipsis unsafeHTML={highlightSnippet} />
      );
      break;
    case "quotes.quote": {
      content = (
        // <blockquote className="blockquote">
        <div>
          {(highlightSnippet && ( // TODO: Replace Regex with more formal fix
            <HighlightEllipsis unsafeHTML={highlightSnippet} />
          )) ??
            (module.bite && <HTMLEllipsis unsafeHTML={module.bite} maxLine="4" basedOn="words" />)}
        </div>
        // </blockquote>
      );
      break;
    }
    case "sources.source":
      content = <div dangerouslySetInnerHTML={{ __html: module.citationHtml }} />;
      break;
    case "entities.person":
    case "entities.organization":
    case "entities.entity":
    case "entities.group":
      content = highlightSnippet && ( // TODO: Replace Regex with more formal fix
        <HighlightEllipsis unsafeHTML={highlightSnippet} />
      );
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
