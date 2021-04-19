import BaseCard from "./BaseCard";
import ImageCard from "./ImageCard";
import OccurrenceCard from "./OccurrenceCard";
import QuoteCard from "./QuoteCard";


export default function ModuleCard({ module, ...childProps }) {
  // ModuleCard is a generic component for rendering cards of any
  // model type, removing the need to import every card component.
  switch (module["model"]) {
    case "occurrences.occurrence":
      return <OccurrenceCard occurrence={module} {...childProps} />;
    case "quotes.quote":
      return <QuoteCard quote={module} {...childProps} />;
    case "images.image":
      return <ImageCard image={module} {...childProps} />;
    default:
      return <BaseCard module={module} {...childProps} />;
  }
}
