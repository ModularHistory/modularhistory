import PropositionDetail from "@/components/propositions/PropositionDetail";
import { ModuleUnion } from "@/types/modules";
import { useSession } from "next-auth/client";
import { createRef, FC, useLayoutEffect } from "react";
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
  const ref = createRef<HTMLDivElement>();
  const [session, loading] = useSession();
  useLayoutEffect(() => {
    // After the DOM has rendered, check for lazy images
    // and set their `src` to the correct value.
    // This is not an optimal solution, and will likely change
    // after redesigning how backend HTML is served.
    const images = (ref.current as HTMLDivElement).getElementsByTagName("img");

    for (const img of images) {
      if (img.dataset["src"]) img.src = img.dataset["src"];
    }
  }, [ref]);

  let details;
  switch (module.model) {
    // TODO: add more models here as soon as they
    //       may appear on the SERP.
    case "entities.entity":
    case "entities.person":
    case "entities.organization":
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
