import BaseCard from "./BaseCard";

export default function OccurrenceCard({ occurrence, ...childProps }) {
  // Mostly copied from `apps/occurrences/templates/occurrences/_card.html`
  return (
    <BaseCard module={occurrence} {...childProps}>
      <div
        className="card-text text-center"
        dangerouslySetInnerHTML={{ __html: occurrence["summary"] }}
      />
    </BaseCard>
  );
}
