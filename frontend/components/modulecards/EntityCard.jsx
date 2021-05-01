import BaseCard from "./BaseCard";

export default function EntityCard({ entity, ...childProps }) {
  return (
    <BaseCard module={entity} {...childProps}>
      <div
        className="card-text text-center"
        dangerouslySetInnerHTML={{ __html: entity["truncated_description"] }}
      />
    </BaseCard>
  );
}
