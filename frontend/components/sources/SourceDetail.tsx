import { Source } from "@/interfaces";
import { FC } from "react";
import TagList from "../topics/TagList";

interface SourceDetailProps {
  source: Source;
}

const SourceDetail: FC<SourceDetailProps> = ({ source }: SourceDetailProps) => {
  const titleHtml = source.title || source.citationString;
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: titleHtml }} />
      <div dangerouslySetInnerHTML={{ __html: source.citationHtml }} />
      {!!source.cachedTags?.length && <TagList topics={source.cachedTags} />}
    </>
  );
};

export default SourceDetail;
