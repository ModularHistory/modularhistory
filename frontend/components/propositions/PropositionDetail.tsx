import ModuleHTML from "@/components/details/ModuleHTML";
import TagList from "@/components/topics/TagList";
import { Proposition } from "@/types/models";
import { Box } from "@mui/material";
import Slider from "@mui/material/Slider";
import { useSession } from "next-auth/client";
import { FC } from "react";
import ArgumentSet from "./ArgumentSet";

interface PropositionDetailProps {
  proposition: Proposition;
}

const strengthTextValues = [
  "No credible evidence",
  "Some credible evidence",
  "A preponderance of evidence",
  "Beyond reasonable doubt",
  "Beyond any shadow of a doubt",
];

function getValueText(value: number) {
  return strengthTextValues[value];
}

function getValueLabelFormat(value: number) {
  return strengthTextValues[value];
}

const PropositionDetail: FC<PropositionDetailProps> = ({ proposition }: PropositionDetailProps) => {
  const [session, loading] = useSession();
  const titleHtml = proposition.summary;
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: titleHtml }} />
      {!loading && session?.user?.["isSuperuser"] && (
        <a
          href={proposition.adminUrl}
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
      {Number.isInteger(proposition.certainty) && (
        <div style={{ margin: "3rem 2rem 0" }}>
          <Slider
            defaultValue={proposition.certainty}
            getAriaValueText={getValueText}
            valueLabelFormat={getValueLabelFormat}
            valueLabelDisplay="on"
            step={5}
            min={0}
            max={4}
            marks
            disabled
          />
        </div>
      )}

      <Box m={"1.5rem 0"}>
        <ModuleHTML html={proposition.elaboration} />
      </Box>

      {!!proposition.arguments?.length && <ArgumentSet argumentSet={proposition.arguments} />}
      {proposition.postscript && <p dangerouslySetInnerHTML={{ __html: proposition.postscript }} />}

      {!!proposition.cachedTags?.length && <TagList topics={proposition.cachedTags} />}

      <footer className="footer sources-footer">
        <ol className="citations">
          {proposition.cachedCitations.map((citation) => {
            const id = `citation-${citation.id}`;
            return (
              <li
                className="source"
                id={id}
                key={id}
                dangerouslySetInnerHTML={{ __html: citation.html }}
              />
            );
          })}
        </ol>
      </footer>
    </>
  );
};

export default PropositionDetail;
