import BaseCard from "./BaseCard";

export default function OccurrenceCard({occurrence}) {
  return (
    <BaseCard module={occurrence}>
      <div className="card-text text-center"
           dangerouslySetInnerHTML={{__html: occurrence['summary']}} />
    </BaseCard>
  );
}
