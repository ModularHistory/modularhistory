import HTMLEllipsis from "react-lines-ellipsis/lib/html";
import ImageCard from "./ImageCard";
import ModuleCard from "./ModuleCard";

export default function ModuleUnionCard({ module, ...childProps }) {
  // ModuleUnionCard is a generic component for rendering cards of any
  // model type, removing the need to import every card component.
  let content;
  switch (module["model"]) {
    case "images.image":
      return <ImageCard image={module} {...childProps} />;
    case "occurrences.occurrence":
      content = <div dangerouslySetInnerHTML={{ __html: module["summary"] }} />;
      break;
    case "postulations.postulation":
      content = <div dangerouslySetInnerHTML={{ __html: module["summary"] }} />;
      break;
    case "quotes.quote":
      content = (
        <blockquote className="blockquote">
          <HTMLEllipsis unsafeHTML={module["bite"]} maxLine="4" basedOn="words" />
          {module["attributeeString"] && (
            <footer
              className="blockquote-footer"
              dangerouslySetInnerHTML={{ __html: module["attributeeString"] }}
            />
          )}
        </blockquote>
      );
      break;
    case "sources.source":
      content = <div dangerouslySetInnerHTML={{ __html: module["citationHtml"] }} />;
      break;
  }
  return (
    <ModuleCard module={module} {...childProps}>
      {content}
    </ModuleCard>
  );
}
