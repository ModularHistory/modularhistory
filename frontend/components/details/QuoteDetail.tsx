import { QuoteModule } from "@/interfaces";
import { FC } from "react";
import ImageCard from "../cards/ImageCard";

interface QuoteDetailProps {
  quote: QuoteModule;
}

const QuoteDetail: FC<QuoteDetailProps> = ({ quote }: QuoteDetailProps) => {
  let titleHtml = quote["attributee_html"];
  if (quote["dateHtml"]) {
    titleHtml += (titleHtml ? ", " : "") + quote["dateHtml"];
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
};

export default QuoteDetail;
