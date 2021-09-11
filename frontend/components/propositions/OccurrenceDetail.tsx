import { Occurrence } from "@/types/modules";
import { FC } from "react";
import { titleCase } from "title-case";
import ImageCard from "../images/ImageCard";
import TagList from "../topics/TagList";

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
      {occurrence.cachedImages?.map(
        (image, index) =>
          occurrence.elaboration.includes(image.srcUrl) || (
            <div className="img-container" style={{ maxWidth: "44%" }} key={index}>
              <ImageCard image={image} />
            </div>
          )
      )}

      <h2 className="text-center my-3">{titleCase(occurrence.title)}</h2>
      {occurrence.summary != occurrence.title && (
        <p className="lead" dangerouslySetInnerHTML={{ __html: occurrence.summary }} />
      )}
      <div dangerouslySetInnerHTML={{ __html: occurrence.elaboration }} />
      {occurrence.postscript && <p dangerouslySetInnerHTML={{ __html: occurrence.postscript }} />}

      {!!occurrence.cachedTags?.length && <TagList topics={occurrence.cachedTags} />}

      <footer className="footer sources-footer">
        <ol className="citations">
          {occurrence.cachedCitations.map((citation) => {
            const id = `citation-${citation.id}`;
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
