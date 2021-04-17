import ImageCard from "../modulecards/ImageCard";

export default function QuoteDetail({ quote }) {
  let titleHtml = quote["attributee_html"];
  if (quote["date_html"]) {
    titleHtml += (titleHtml ? ", " : "") + quote["date_html"];
  }

  const firstImage = quote["serialized_images"]?.[0];

  return (
    <>
      <h2 className="text-center card-title" dangerouslySetInnerHTML={{ __html: titleHtml }} />

      <div className="card-text">
        {firstImage && (
          <div className="img-container" style={{ maxWidth: "44%" }}>
            <ImageCard image={firstImage} />
          </div>
        )}

        <div dangerouslySetInnerHTML={{ __html: quote["html"] }} />

        {quote["tags_html"] && (
          <ul className="tags" dangerouslySetInnerHTML={{ __html: quote["tags_html"] }} />
        )}

        <footer className="footer sources-footer">
          <ol className="citations">
            {quote["serialized_citations"].map((citation) => (
              <li
                key={citation["pk"]}
                className="source"
                id={`citation-${citation["pk"]}`}
                dangerouslySetInnerHTML={{ __html: citation["html"] }}
              />
            ))}
          </ol>
        </footer>
      </div>
    </>
  );
}
