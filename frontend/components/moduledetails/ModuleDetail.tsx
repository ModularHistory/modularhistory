import { EntityModule, OccurrenceModule, QuoteModule } from "@/interfaces";
import { useSession } from "next-auth/client";
import { createRef, FC, useLayoutEffect } from "react";
import EntityDetail from "./EntityDetail";
import OccurrenceDetail from "./OccurrenceDetail";
import QuoteDetail from "./QuoteDetail";

interface ModuleDetailProps {
  module: OccurrenceModule | QuoteModule | EntityModule;
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
    // force switching between modules to scroll
    // to the top of the new module
    ref.current.parentElement.scrollTop = 0;
  }, [module]);

  let details;
  switch (module["model"]) {
    // TODO: add more models here as soon as they
    //       may appear on the SERP.
    case "occurrences.occurrence":
      details = <OccurrenceDetail occurrence={module as OccurrenceModule} />;
      break;
    case "quotes.quote":
      details = <QuoteDetail quote={module as QuoteModule} />;
      break;
    case "entities.entity":
    case "entities.person":
      details = <EntityDetail entity={module as EntityModule} />;
      break;
    default:
      details = <pre>{JSON.stringify(module)}</pre>;
  }

  return (
    <div className="detail" ref={ref}>
      {!loading && session?.user?.["is_superuser"] && (
        <a
          href={module["admin_url"] || module["adminUrl"]}
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
