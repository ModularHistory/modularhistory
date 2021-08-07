import { Source } from "@/interfaces";
import { FC } from "react";
import Tag from "../topics/Tag";

interface SourceDetailProps {
  source: Source;
}

const SourceDetail: FC<SourceDetailProps> = ({ source }: SourceDetailProps) => {
  const titleHtml = source.title || source.citationString;
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: titleHtml }} />
      <div dangerouslySetInnerHTML={{ __html: source.citationHtml }} />
      {!!source.cachedTags?.length && (
        <ul className="tags">
          {source.cachedTags.map((topic) => (
            <Tag key={topic.pk} topic={topic} />
          ))}
        </ul>
      )}
    </>
  );
};

export default SourceDetail;
