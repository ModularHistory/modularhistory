import BaseCard from "./BaseCard";

export default function OccurrenceCard({occurrence, ...childProps}) {
  return (
    <BaseCard module={occurrence} {...childProps}>
      <div className="card-text text-center"
           dangerouslySetInnerHTML={{__html: occurrence['summary']}} />
    </BaseCard>
  );
}
