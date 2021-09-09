import { ModuleUnion, Topic } from "@/types/modules";
import { Box } from "@material-ui/system";
import React, { FC } from "react";
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
      content = module.meta &&
        module.meta.highlight &&
        module.meta.highlight.text &&
        module.meta.highlight.text.length > 0 && ( // TODO: Replace Regex with more formal fix
          <Box
            sx={{
              "& *": { fontSize: "0.8rem", backgroundColor: "rgba(0, 0, 0, 0)" },
              "& mark": { fontWeight: "500", color: "white" },
            }}
          >
            <HTMLEllipsis
              unsafeHTML={module.meta.highlight.text[0].replace(/(<(h[1-6])>.*?<\/h[1-6]>)/gi, "")}
              maxLine="4"
              basedOn="words"
            />
          </Box>
        );
      break;
    case "propositions.proposition":
      content = module.meta &&
        module.meta.highlight &&
        module.meta.highlight.text &&
        module.meta.highlight.text.length > 0 && ( // TODO: Replace Regex with more formal fix
          <Box
            sx={{
              "& *": { fontSize: "0.8rem", backgroundColor: "rgba(0, 0, 0, 0)" },
              "& mark": { fontWeight: "500", color: "white" },
            }}
          >
            <HTMLEllipsis
              unsafeHTML={module.meta.highlight.text[0].replace(/(<(h[1-6])>.*?<\/h[1-6]>)/gi, "")}
              maxLine="4"
              basedOn="words"
            />
          </Box>
        );
      break;
    case "quotes.quote": {
      content = (
        // <blockquote className="blockquote">
        <div>
          {(module.meta &&
            module.meta.highlight &&
            module.meta.highlight.text &&
            module.meta.highlight.text.length > 0 && ( // TODO: Replace Regex with more formal fix
              <Box
                sx={{
                  "& *": { fontSize: "0.8rem", backgroundColor: "rgba(0, 0, 0, 0)" },
                  "& mark": { fontWeight: "500", color: "white" },
                }}
              >
                <HTMLEllipsis
                  unsafeHTML={module.meta.highlight.text[0].replace(
                    /(<(h[1-6])>.*?<\/h[1-6]>)/gi,
                    ""
                  )}
                  maxLine="4"
                  basedOn="words"
                />
              </Box>
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
      content = module.meta &&
        module.meta.highlight &&
        module.meta.highlight.text &&
        module.meta.highlight.text.length > 0 && ( // TODO: Replace Regex with more formal fix
          <Box
            sx={{
              "& *": { fontSize: "0.8rem", backgroundColor: "rgba(0, 0, 0, 0)" },
              "& mark": { fontWeight: "500", color: "white" },
            }}
          >
            <HTMLEllipsis
              unsafeHTML={module.meta.highlight.text[0].replace(/(<(h[1-6])>.*?<\/h[1-6]>)/gi, "")}
              maxLine="4"
              basedOn="words"
            />
          </Box>
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
