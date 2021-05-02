import BaseCard from "./BaseCard";
import ImageCard from "./ImageCard";

export default function ModuleCard({ module, ...childProps }) {
  // ModuleCard is a generic component for rendering cards of any
  // model type, removing the need to import every card component.
  let content = <div />;
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
        <>
          <blockquote className="blockquote">
            <div dangerouslySetInnerHTML={{ __html: module["truncated_html"] }} />
            <footer
              className="blockquote-footer"
              dangerouslySetInnerHTML={{ __html: module["attributee_string"] }}
            />
          </blockquote>
        </>
      );
      break;
    case "sources.source":
      content = <div dangerouslySetInnerHTML={{ __html: module["citationHtml"] }} />;
      break;
    default:
      return <BaseCard module={module} content={content} {...childProps} />;
  }
  return <BaseCard module={module} content={content} {...childProps} />;
}
