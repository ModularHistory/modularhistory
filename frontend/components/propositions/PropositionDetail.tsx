import { Proposition } from "@/interfaces";
import { Theme } from "@material-ui/core";
import Slider from "@material-ui/core/Slider";
import { createStyles, makeStyles } from "@material-ui/styles";
import { useSession } from "next-auth/client";
import { FC } from "react";
import ArgumentSet from "./ArgumentSet";

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      width: "100%",
    },
    heading: {
      fontSize: theme.typography.pxToRem(15),
      fontWeight: theme.typography.fontWeightRegular,
    },
    tree: {
      flexGrow: 1,
    },
  })
);

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
      <div
        dangerouslySetInnerHTML={{ __html: proposition.elaboration }}
        style={{ margin: "1.5rem 0" }}
      />
      {proposition.arguments && !!proposition.arguments.length && (
        <ArgumentSet argumentSet={proposition.arguments} />
      )}
    </>
  );
};

export default PropositionDetail;
