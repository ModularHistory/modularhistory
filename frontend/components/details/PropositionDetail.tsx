import { Proposition } from "@/interfaces";
import Accordion from "@material-ui/core/Accordion";
import AccordionDetails from "@material-ui/core/AccordionDetails";
import AccordionSummary from "@material-ui/core/AccordionSummary";
import { createStyles, makeStyles, Theme } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import { FC } from "react";

interface PropositionDetailProps {
  proposition: Proposition;
}

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      width: "100%",
    },
    heading: {
      fontSize: theme.typography.pxToRem(15),
      fontWeight: theme.typography.fontWeightRegular,
    },
  })
);

const PropositionDetail: FC<PropositionDetailProps> = ({ proposition }: PropositionDetailProps) => {
  const classes = useStyles();
  const titleHtml = proposition.summary;
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: titleHtml }} />
      <div dangerouslySetInnerHTML={{ __html: proposition.elaboration }} />
      <div className={classes.root}>
        {proposition.arguments &&
          proposition.arguments.map((argument) => (
            <div key={argument.pk}>
              <p dangerouslySetInnerHTML={{ __html: argument.explanation }} />
              {argument.premises.map((premise) => (
                <Accordion key={argument.pk}>
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon />}
                    aria-controls="panel1a-content"
                    id="panel1a-header"
                  >
                    <Typography className={classes.heading}>{premise.summary}</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <div dangerouslySetInnerHTML={{ __html: premise.elaboration }} />
                  </AccordionDetails>
                </Accordion>
              ))}
            </div>
          ))}
      </div>
    </>
  );
};

export default PropositionDetail;
