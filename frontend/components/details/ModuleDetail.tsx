import PropositionDetail from "@/components/propositions/PropositionDetail";
import { ModuleUnion } from "@/types/modules";
import BookmarksIcon from "@mui/icons-material/Bookmarks";
import { useSession } from "next-auth/client";
import { FC } from "react";
import EntityDetail from "../entities/EntityDetail";
import ImageDetail from "../images/ImageDetail";
import OccurrenceDetail from "../propositions/OccurrenceDetail";
import QuoteDetail from "../quotes/QuoteDetail";
import SourceDetail from "../sources/SourceDetail";
import TopicDetail from "../topics/TopicDetail";

interface ModuleDetailProps {
  module: ModuleUnion;
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
    case "entities.group":
      details = <EntityDetail entity={module} />;
      break;
    case "images.image":
      details = <ImageDetail image={module} />;
      break;
    case "propositions.occurrence":
      details = <OccurrenceDetail occurrence={module} />;
      break;
    case "propositions.proposition":
      details = <PropositionDetail proposition={module} />;
      break;
    case "quotes.quote":
      details = <QuoteDetail quote={module} />;
      break;
    case "sources.source":
    case "sources.article":
    case "sources.book":
    case "sources.correspondence":
    case "sources.document":
    case "sources.speech":
      details = <SourceDetail source={module} />;
      break;
    case "topics.topic":
      details = <TopicDetail topic={module} />;
      break;
    default:
      ((module: never) => {
        throw new Error(`Unexpected module type encountered: ${(module as any).model}`);
      })(module);
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
      <div
        className="bookmark"
        style={{
          display: "flex",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <BookmarksIcon
          style={{
            fontSize: "25px",
          }}
        />
        <span>&nbsp;Save</span>
      </div>
      {details}
    </div>
  );
};

export default ModuleDetail;
