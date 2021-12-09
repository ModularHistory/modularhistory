import Citation from "@/components/sources/Citation";
import { Source } from "@/types/models";
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
      <Citation html={source.citationHtml} />
      {!!source.cachedTags?.length && <TagList topics={source.cachedTags} />}
    </>
  );
};

export default SourceDetail;
