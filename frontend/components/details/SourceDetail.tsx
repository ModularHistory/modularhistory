import { Source } from "@/interfaces";
import { FC } from "react";

interface SourceDetailProps {
  source: Source;
}

const SourceDetail: FC<SourceDetailProps> = ({ source }: SourceDetailProps) => {
  let titleHtml = source.title || source.citationString;
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: titleHtml }} />
      <div dangerouslySetInnerHTML={{ __html: source.citationHtml }} />
      {source.tagsHtml && (
        <ul className="tags" dangerouslySetInnerHTML={{ __html: source.tagsHtml }} />
      )}
    </>
  );
};

export default SourceDetail;
