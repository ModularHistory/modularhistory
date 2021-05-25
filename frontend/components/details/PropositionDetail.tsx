import { PropositionModule } from "@/interfaces";
import { FC } from "react";

interface PropositionDetailProps {
  proposition: PropositionModule;
}

const PropositionDetail: FC<PropositionDetailProps> = ({ proposition }: PropositionDetailProps) => {
  let titleHtml = proposition.summary;
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: titleHtml }} />
      <div dangerouslySetInnerHTML={{ __html: proposition.elaboration }} />
    </>
  );
};

export default PropositionDetail;
