import ModuleHTML from "@/components/details/ModuleHTML";
import { Quote } from "@/types/models";
import { FC } from "react";
import ImageCard from "../images/ImageCard";
import TagList from "../topics/TagList";

interface QuoteDetailProps {
  quote: Quote;
}

const QuoteDetail: FC<QuoteDetailProps> = ({ quote }: QuoteDetailProps) => {
  const titleHtml = [quote.attributeeHtml, quote.dateString].filter(Boolean).join(", ");
  const firstImage = quote.cachedImages?.[0];
  return (
    <>
      <h2 className="text-center card-title" dangerouslySetInnerHTML={{ __html: titleHtml }} />

      {firstImage && (
        <div className="img-container" style={{ maxWidth: "44%" }}>
          <ImageCard image={firstImage} />
        </div>
      )}

      <ModuleHTML html={quote.html} />

      {!!quote.cachedTags?.length && <TagList topics={quote.cachedTags} />}

      <footer className="footer sources-footer">
        <ol className="citations">
          {quote.cachedCitations.map((citation) => (
            <li
              key={citation.id}
              className="source"
              id={`citation-${citation.id}`}
              dangerouslySetInnerHTML={{ __html: citation.html }}
            />
          ))}
        </ol>
      </footer>
    </>
  );
};

export default QuoteDetail;
