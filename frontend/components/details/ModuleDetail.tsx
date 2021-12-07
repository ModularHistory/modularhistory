import axiosWithAuth from "@/axiosWithAuth";
import PropositionDetail from "@/components/propositions/PropositionDetail";
import { ModuleUnion } from "@/types/modules";
import BookmarkBorderIcon from "@mui/icons-material/BookmarkBorder";
import BookmarksIcon from "@mui/icons-material/Bookmarks";
import Button from "@mui/material/Button";
import { useSession } from "next-auth/client";
import { FC, useState } from "react";
import EntityDetail from "../entities/EntityDetail";
import ImageDetail from "../images/ImageDetail";
import OccurrenceDetail from "../propositions/OccurrenceDetail";
import QuoteDetail from "../quotes/QuoteDetail";
import SourceDetail from "../sources/SourceDetail";
import TopicDetail from "../topics/TopicDetail";
interface ModuleDetailProps {
  module: ModuleUnion;
}

const TYPE_MAP: Record<string, string> = {
  "entities.entity": "entities",
  "propositions.proposition": "propositions",
  "propositions.occurrence": "propositions",
  "quotes.quote": "quotes",
  "sources.source": "sources",
};

const ModuleDetail: FC<ModuleDetailProps> = ({ module }: ModuleDetailProps) => {
  const [session, loading] = useSession();
  // TODO: We need to make a query to determine if the module is already saved by the user
  // instead of just initially setting the state to false.
  const [isSaved, setIsSaved] = useState(false);
  let details;

  const saveCollectionItem = async () => {
    if (session?.user) {
      const key: string | undefined = TYPE_MAP[module.model];
      if (key) {
        await axiosWithAuth
          .post("/api/collections/add_items", {
            data: {
              [key]: [module.id],
            },
          })
          .then(function (response) {
            console.log(JSON.stringify(response.data));
            setIsSaved(true);
          })
          .catch(function (error) {
            console.log(error);
          });
      }
    }
    return null;
  };

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

      <Button onClick={saveCollectionItem}>
        {isSaved ? (
          <BookmarksIcon
            style={{
              fontSize: "25px",
            }}
          />
        ) : (
          <BookmarkBorderIcon
            style={{
              fontSize: "25px",
            }}
          />
        )}
        <span>&nbsp;Save</span>
      </Button>
      {details}
    </div>
  );
};

export default ModuleDetail;
