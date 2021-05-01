import BaseCard from "./BaseCard";

export default function SourceCard({ source, ...childProps }) {
  return (
    <BaseCard module={source} {...childProps}>
      <div
        className="card-text text-center"
        dangerouslySetInnerHTML={{ __html: source["citationHtml"] }}
      />
    </BaseCard>
  );
}
