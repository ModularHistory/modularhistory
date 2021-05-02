import BaseCard from "./BaseCard";
import ImageCard from "./ImageCard";
import QuoteCard from "./QuoteCard";

export default function ModuleCard({ module, ...childProps }) {
  // ModuleCard is a generic component for rendering cards of any
  // model type, removing the need to import every card component.
  switch (module["model"]) {
    case "images.image":
      return <ImageCard image={module} {...childProps} />;
    case "occurrences.occurrence":
      return <BaseCard module={module} content={occurrence["summary"]} {...childProps} />;
    case "postulations.postulation":
      return <BaseCard module={module} content={postulation["summary"]} {...childProps} />;
    case "quotes.quote":
      return <QuoteCard quote={module} {...childProps} />;
    case "sources.source":
      return <BaseCard module={module} content={source["citationHtml"]} {...childProps} />;
    default:
      return <BaseCard module={module} {...childProps} />;
  }
}
