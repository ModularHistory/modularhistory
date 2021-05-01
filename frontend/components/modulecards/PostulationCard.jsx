import BaseCard from "./BaseCard";

export default function PostulationCard({ postulation, ...childProps }) {
  return (
    <BaseCard module={postulation} {...childProps}>
      <div
        className="card-text text-center"
        dangerouslySetInnerHTML={{ __html: postulation["summary"] }}
      />
    </BaseCard>
  );
}
