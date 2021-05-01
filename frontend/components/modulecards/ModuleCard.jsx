import BaseCard from "./BaseCard";
import ImageCard from "./ImageCard";
import OccurrenceCard from "./OccurrenceCard";
import PostulationCard from "./PostulationCard";
import QuoteCard from "./QuoteCard";

export default function ModuleCard({ module, ...childProps }) {
  // ModuleCard is a generic component for rendering cards of any
  // model type, removing the need to import every card component.
  switch (module["model"]) {
    case "images.image":
      return <ImageCard image={module} {...childProps} />;
    case "occurrences.occurrence":
      return <OccurrenceCard occurrence={module} {...childProps} />;
    case "postulations.postulation":
      return <PostulationCard image={module} {...childProps} />;
    case "quotes.quote":
      return <QuoteCard quote={module} {...childProps} />;
    case "sources.source":
      return <SourceCard image={module} {...childProps} />;
    default:
      return <BaseCard module={module} {...childProps} />;
  }
}
