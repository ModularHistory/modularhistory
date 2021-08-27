import PropositionDetail from "@/components/propositions/PropositionDetail";
import { Entity, Image, Occurrence, Proposition, Quote, Source, Topic } from "@/interfaces";
import { useSession } from "next-auth/client";
import { FC } from "react";
import EntityDetail from "../entities/EntityDetail";
import ImageDetail from "../images/ImageDetail";
import OccurrenceDetail from "../propositions/OccurrenceDetail";
import QuoteDetail from "../quotes/QuoteDetail";
import SourceDetail from "../sources/SourceDetail";
import TopicDetail from "../topics/TopicDetail";

interface ModuleDetailProps {
  module: Occurrence | Quote | Entity | Topic | Proposition | Image | Source;
}

const ModuleDetail: FC<ModuleDetailProps> = ({ module }: ModuleDetailProps) => {
  const [session, loading] = useSession();
  let details;
  switch (module.model) {
    // TODO: add more models here as soon as they
    //       may appear on the SERP.
    case "entities.entity":
    case "entities.person":
    case "entities.organization":
      details = <EntityDetail entity={module as Entity} />;
      break;
    case "images.image":
      details = <ImageDetail image={module as Image} />;
      break;
    case "propositions.occurrence":
      details = <OccurrenceDetail occurrence={module as Occurrence} />;
      break;
    case "propositions.proposition":
      details = <PropositionDetail proposition={module as Proposition} />;
      break;
    case "quotes.quote":
      details = <QuoteDetail quote={module as Quote} />;
      break;
    case "sources.source":
      details = <SourceDetail source={module as Source} />;
      break;
    case "topics.topic":
      details = <TopicDetail topic={module as Topic} />;
      break;
    default:
      throw new Error(`Unknown module type encountered: ${module.model}`);
  }

  return (
    <div className="detail">
      {!loading && session?.user?.["isSuperuser"] && (
        <a
          href={module.adminUrl}
          target="_blank"
          className="edit-object-button"
          rel="noopener noreferrer"
          style={{
            display: "inline-block",
            position: "absolute",
            top: "1px",
            right: "-2rem",
            fontWeight: "bold",
          }}
        >
          <i className="fa fa-edit" />
        </a>
      )}
      {details}
    </div>
  );
};

export default ModuleDetail;
