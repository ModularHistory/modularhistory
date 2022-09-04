import { ModuleUnion, Topic } from "@/types/modules";
import { Box } from "@mui/material";
import React, { FC } from "react";
import HTMLEllipsis from "react-lines-ellipsis/lib/html";
import ModuleCard, { ModuleCardProps } from "./ModuleCard";

interface HighlightEllipsisProps {
  unsafeHTML: string;
}

function applyHTMLFilter(unsafeHTML: string) {
  // TODO: Replace regex with more formal fix
  return `${unsafeHTML}`.replace(
    /(<(h[1-6])>.*?<\/h[1-6]>)|(<p><\/p>)|(<div><\/div>)|(<\/?p>)|(<\/?div>)|(<module[^>]*?>.*?<\/module>)|(<\/?blockquote[^>]*?>)/gi,
    ""
  );
  //Removing <h>, <p>, <div>, <module> (for images), and <blockquote> tags from content snippet
}

const HighlightEllipsis: FC<HighlightEllipsisProps> = ({ unsafeHTML }) => (
  <Box
    sx={{
      "& *": { fontSize: "0.8rem", backgroundColor: "rgba(0, 0, 0, 0)", display: "inline" },
      "& > div > div::before": { content: '"... "' }, // ellipses with trailing space
      "& > div > div::after": { content: '" ..."' }, // ellipses with leading space
      "& p::before": { content: '"... "' }, // ellipses with trailing space
      "& p::after": { content: '" ..."' }, // ellipses with leading space
      "& mark": { fontWeight: "500", color: "white" },
    }}
  >
    <HTMLEllipsis unsafeHTML={applyHTMLFilter(unsafeHTML)} maxLine="3" basedOn="words" />
  </Box>
);

interface ModuleUnionCardProps extends ModuleCardProps {
  module: Exclude<ModuleUnion, Topic>;
}

const ModuleUnionCard: FC<ModuleUnionCardProps> = ({
  module,
  ...childProps
}: ModuleUnionCardProps) => {
  // ModuleUnionCard is a generic component for rendering cards of any
  // model type, removing the need to import every card component.
  let content;
  const highlightSnippet =
    module?.meta?.highlight?.text?.[0] ??
    module?.meta?.highlight?.description?.[0] ??
    module?.meta?.highlight?.elaboration?.[0]; // highlight text, description, or elaboration
  switch (module.model) {
    case "images.image":
      // return <ImageCard image={module} {...childProps} />;
      content = (
        <HTMLEllipsis
          unsafeHTML={applyHTMLFilter(module.captionHtml)}
          maxLine="3"
          basedOn="words"
        />
      );
      break;
    case "propositions.occurrence":
      content = (highlightSnippet && <HighlightEllipsis unsafeHTML={highlightSnippet} />) || (
        <HTMLEllipsis
          unsafeHTML={applyHTMLFilter(module.truncatedElaboration ?? module.elaboration)}
          maxLine="2"
          basedOn="words"
        />
      );
      break;
    case "propositions.proposition":
    case "propositions.conclusion":
      content = (highlightSnippet && <HighlightEllipsis unsafeHTML={highlightSnippet} />) || (
        <HTMLEllipsis
          unsafeHTML={applyHTMLFilter(module.elaboration)}
          maxLine="2"
          basedOn="words"
        />
      );
      break;
    case "quotes.quote": {
      content = (
        <div>
          {(highlightSnippet && <HighlightEllipsis unsafeHTML={highlightSnippet} />) ??
            (module.bite && (
              <HTMLEllipsis unsafeHTML={applyHTMLFilter(module.bite)} maxLine="3" basedOn="words" />
            ))}
        </div>
      );
      break;
    }
    case "sources.source":
    case "sources.article":
    case "sources.book":
    case "sources.correspondence":
    case "sources.document":
    case "sources.speech":
    case "sources.webpage":
      content = (
        <div>{module.citationHtml && <HighlightEllipsis unsafeHTML={module.citationHtml} />}</div>
      );
      break;
    case "entities.entity":
    case "entities.person":
    case "entities.organization":
    case "entities.group":
      content = (highlightSnippet && <HighlightEllipsis unsafeHTML={highlightSnippet} />) || (
        <HTMLEllipsis
          unsafeHTML={applyHTMLFilter(module.truncatedDescription)}
          maxLine="3"
          basedOn="words"
        />
      );
      break;
    default:
      ((module: unknown) => {
        throw new Error(`Unexpected module type encountered: ${(module as any).model}`);
      })(module);
  }
  return (
    <ModuleCard module={module} {...childProps}>
      {content}
    </ModuleCard>
  );
};

export default ModuleUnionCard;
