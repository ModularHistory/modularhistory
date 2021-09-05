import { Occurrence } from "@/types/modules";
import { FC } from "react";
import ImageCard from "../images/ImageCard";
import TagList from "../topics/TagList";

interface OccurrenceDetailProps {
  occurrence: Occurrence;
}

function titleCase(word: string) {
  let i, j;
  word = word.replace(/([^\W_]+[^\s-]*) */g, function (text: string) {
    if (!/[a-z]/.test(text) && /[A-Z]/.test(text)) {
      return text;
    } else {
      return text.charAt(0).toUpperCase() + text.substr(1);
    }
  });
  const lowerCase: string[] = [
    "A",
    "An",
    "And",
    "As",
    "At",
    "But",
    "By",
    "For",
    "From",
    "In",
    "Into",
    "Near",
    "Nor",
    "Of",
    "On",
    "Onto",
    "Or",
    "The",
    "To",
    "With",
  ];

  for (i = 0, j = lowerCase.length; i < j; i++)
    word = word.replace(new RegExp("\\s" + lowerCase[i] + "\\s", "g"), function (text: string) {
      return text.toLowerCase();
    });

  return word;
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

      <h2
        className="text-center my-3"
        dangerouslySetInnerHTML={{ __html: titleCase(occurrence.title) }}
      />
      {occurrence.summary != occurrence.title && <p className="lead">{occurrence.summary}</p>}
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
