import { Occurrence } from "@/interfaces";
import { FC } from "react";
import ImageCard from "../images/ImageCard";

interface OccurrenceDetailProps {
  occurrence: Occurrence;
}

const OccurrenceDetail: FC<OccurrenceDetailProps> = ({ occurrence }: OccurrenceDetailProps) => {
  return (
    <>
      {occurrence.verified || (
        <span
          style={{
            display: "inline-block",
            position: "absolute",
            top: "1px",
            right: "1px",
            fontWeight: "bold",
          }}
        >
          UNVERIFIED
        </span>
      )}
      <p
        className="text-center card-title lead"
        dangerouslySetInnerHTML={{ __html: occurrence.dateString }}
      />
      {occurrence.cachedImages.map(
        (image, index) =>
          occurrence.elaboration.includes(image.srcUrl) || (
            <div className="img-container" style={{ maxWidth: "44%" }} key={index}>
              <ImageCard image={image} />
            </div>
          )
      )}

      <h2 className="text-center my-3" dangerouslySetInnerHTML={{ __html: occurrence.title }} />
      {occurrence.summary != occurrence.title && <p className="lead">{occurrence.summary}</p>}
      <div dangerouslySetInnerHTML={{ __html: occurrence.elaboration }} />
      {occurrence.postscript && <p dangerouslySetInnerHTML={{ __html: occurrence.postscript }} />}
      {occurrence.tagsHtml && (
        <ul className="tags" dangerouslySetInnerHTML={{ __html: occurrence.tagsHtml }} />
      )}

      <footer className="footer sources-footer">
        <ol className="citations">
          {occurrence.cachedCitations.map((citation) => {
            const id = `citation-${citation.pk}`;
            return (
              <li
                className="source"
                id={id}
                key={id}
                dangerouslySetInnerHTML={{ __html: citation.html }}
              />
            );
          })}
        </ol>
      </footer>
    </>
  );
};

export default OccurrenceDetail;
