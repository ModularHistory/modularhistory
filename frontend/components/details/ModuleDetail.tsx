import PropositionDetail from "@/components/propositions/PropositionDetail";
import { Entity, Image, Occurrence, Proposition, Quote, Source, Topic } from "@/interfaces";
import { useSession } from "next-auth/client";
import { createRef, FC, useLayoutEffect } from "react";
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
  const ref = createRef<HTMLDivElement>();
  const [session, loading] = useSession();
  useLayoutEffect(() => {
    // After the DOM has rendered, check for lazy images
    // and set their `src` to the correct value.
    // This is not an optimal solution, and will likely change
    // after redesigning how backend HTML is served.
    const images = ref.current.getElementsByTagName("img");

    for (const img of images) {
      if (img.dataset["src"]) img.src = img.dataset["src"];
    }
  }, [ref]);

  let details;
  switch (module.model) {
    // TODO: add more models here as soon as they
    //       may appear on the SERP.
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
    <div className="detail" ref={ref}>
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
