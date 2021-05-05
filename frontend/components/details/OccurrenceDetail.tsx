import { OccurrenceModule } from "@/interfaces";
import { FC } from "react";
import ImageCard from "../cards/ImageCard";

interface OccurrenceDetailProps {
  occurrence: OccurrenceModule;
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
        dangerouslySetInnerHTML={{ __html: occurrence.dateHtml }}
      />
      {occurrence.serializedImages.map(
        (image) =>
          occurrence.description.includes(image.srcUrl) || (
            <div className="img-container" style={{ maxWidth: "44%" }} key={image.srcUrl}>
              <ImageCard image={image} />
            </div>
          )
      )}

      <h2 className="text-center my-3" dangerouslySetInnerHTML={{ __html: occurrence.summary }} />
      <div dangerouslySetInnerHTML={{ __html: occurrence.description }} />

      {occurrence.postscript && <p dangerouslySetInnerHTML={{ __html: occurrence.postscript }} />}
      {occurrence.tagsHtml && (
        <ul className="tags" dangerouslySetInnerHTML={{ __html: occurrence.tagsHtml }} />
      )}

      <footer className="footer sources-footer">
        <ol className="citations">
          {occurrence.serializedCitations.map((citation) => {
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
