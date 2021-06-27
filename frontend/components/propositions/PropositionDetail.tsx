import ModuleContainer from "@/components/details/ModuleContainer";
import { Proposition } from "@/interfaces";
import { alpha, Button, Theme } from "@material-ui/core";
import Collapse from "@material-ui/core/Collapse";
import Slider from "@material-ui/core/Slider";
import SvgIcon, { SvgIconProps } from "@material-ui/core/SvgIcon";
import { TransitionProps } from "@material-ui/core/transitions";
import { TreeItem, TreeView } from "@material-ui/lab";
import { TreeItemProps } from "@material-ui/lab/TreeItem";
import { createStyles, makeStyles, withStyles } from "@material-ui/styles";
import { animated, useSpring } from "@react-spring/web";
import { useSession } from "next-auth/client";
import Link from "next/link";
import { FC } from "react";
import InlineProposition from "./InlineProposition";

function MinusSquare(props: SvgIconProps) {
  return (
    <SvgIcon fontSize="inherit" style={{ width: 14, height: 14 }} {...props}>
      {/* tslint:disable-next-line: max-line-length */}
      <path d="M22.047 22.074v0 0-20.147 0h-20.12v0 20.147 0h20.12zM22.047 24h-20.12q-.803 0-1.365-.562t-.562-1.365v-20.147q0-.776.562-1.351t1.365-.575h20.147q.776 0 1.351.575t.575 1.351v20.147q0 .803-.575 1.365t-1.378.562v0zM17.873 11.023h-11.826q-.375 0-.669.281t-.294.682v0q0 .401.294 .682t.669.281h11.826q.375 0 .669-.281t.294-.682v0q0-.401-.294-.682t-.669-.281z" />
    </SvgIcon>
  );
}

function PlusSquare(props: SvgIconProps) {
  return (
    <SvgIcon fontSize="inherit" style={{ width: 14, height: 14 }} {...props}>
      {/* tslint:disable-next-line: max-line-length */}
      <path d="M22.047 22.074v0 0-20.147 0h-20.12v0 20.147 0h20.12zM22.047 24h-20.12q-.803 0-1.365-.562t-.562-1.365v-20.147q0-.776.562-1.351t1.365-.575h20.147q.776 0 1.351.575t.575 1.351v20.147q0 .803-.575 1.365t-1.378.562v0zM17.873 12.977h-4.923v4.896q0 .401-.281.682t-.682.281v0q-.375 0-.669-.281t-.294-.682v-4.896h-4.923q-.401 0-.682-.294t-.281-.669v0q0-.401.281-.682t.682-.281h4.923v-4.896q0-.401.294-.682t.669-.281v0q.401 0 .682.281t.281.682v4.896h4.923q.401 0 .682.281t.281.682v0q0 .375-.281.669t-.682.294z" />
    </SvgIcon>
  );
}

function CloseSquare(props: SvgIconProps) {
  return (
    <SvgIcon className="close" fontSize="inherit" style={{ width: 14, height: 14 }} {...props}>
      {/* tslint:disable-next-line: max-line-length */}
      <path d="M17.485 17.512q-.281.281-.682.281t-.696-.268l-4.12-4.147-4.12 4.147q-.294.268-.696.268t-.682-.281-.281-.682.294-.669l4.12-4.147-4.12-4.147q-.294-.268-.294-.669t.281-.682.682-.281.696 .268l4.12 4.147 4.12-4.147q.294-.268.696-.268t.682.281 .281.669-.294.682l-4.12 4.147 4.12 4.147q.294.268 .294.669t-.281.682zM22.047 22.074v0 0-20.147 0h-20.12v0 20.147 0h20.12zM22.047 24h-20.12q-.803 0-1.365-.562t-.562-1.365v-20.147q0-.776.562-1.351t1.365-.575h20.147q.776 0 1.351.575t.575 1.351v20.147q0 .803-.575 1.365t-1.378.562v0z" />
    </SvgIcon>
  );
}

function TransitionComponent(props: TransitionProps) {
  const style = useSpring({
    from: { opacity: 0, transform: "translate3d(20px,0,0)" },
    to: { opacity: props.in ? 1 : 0, transform: `translate3d(${props.in ? 0 : 20}px,0,0)` },
  });

  return (
    <animated.div style={style}>
      <Collapse {...props} />
    </animated.div>
  );
}

const StyledTreeItem = withStyles((theme: Theme) =>
  createStyles({
    iconContainer: {
      "& .close": {
        opacity: 0.3,
      },
    },
    group: {
      marginLeft: 7,
      paddingLeft: 18,
      borderLeft: `1px dashed ${alpha(theme.palette.text.primary, 0.4)}`,
    },
  })
)((props: TreeItemProps) => <TreeItem {...props} TransitionComponent={TransitionComponent} />);

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
  const classes = useStyles();
  const titleHtml = proposition.summary;
  console.log("Certainty is ", proposition.certainty);
  return (
    <ModuleContainer>
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
      {proposition.certainty && (
        <Slider
          style={{ margin: "2.5rem 0 0" }}
          defaultValue={proposition.certainty}
          getAriaValueText={getValueText}
          valueLabelFormat={getValueLabelFormat}
          valueLabelDisplay="on"
          step={5}
          marks
          min={0}
          max={4}
          disabled
        />
      )}
      <div
        dangerouslySetInnerHTML={{ __html: proposition.elaboration }}
        style={{ margin: "1rem 0" }}
      />
      {proposition.arguments && (
        <TreeView
          className={classes.tree}
          defaultExpanded={proposition.arguments.map((argument) => `${argument.pk}`)}
          defaultCollapseIcon={<MinusSquare />}
          defaultExpandIcon={<PlusSquare />}
          defaultEndIcon={<CloseSquare />}
        >
          {proposition.arguments.map((argument, index) => (
            <StyledTreeItem
              key={argument.pk}
              nodeId={`${argument.pk}`}
              label={argument.explanation || `Argument ${index + 1}`}
            >
              {argument.premises &&
                argument.premises.map((premise, subindex) => (
                  <StyledTreeItem
                    key={`${subindex}-${premise.slug}`}
                    nodeId={`${subindex}-${premise.slug}`}
                    label={<InlineProposition proposition={premise} />}
                    style={{ margin: "1rem" }}
                  />
                ))}
            </StyledTreeItem>
          ))}
        </TreeView>
      )}
      {(proposition.conflictingPropositions && (
        <div>
          <h2>Conflicting Propositions</h2>
          {proposition.conflictingPropositions.map((conflictingProposition) => (
            <>
              <p key={conflictingProposition.slug}>
                <Link href={conflictingProposition.absoluteUrl}>
                  {conflictingProposition.summary}
                </Link>
              </p>
              <hr />
            </>
          ))}
        </div>
      )) || (
        <div
          style={{
            marginTop: "2rem",
            borderTop: "1px solid gray",
            textAlign: "center",
            paddingTop: "1rem",
          }}
        >
          <p>This proposition is undisputed.</p>
          <p>
            <Button variant="contained" disabled>
              Dispute
            </Button>
          </p>
        </div>
      )}
    </ModuleContainer>
  );
};

export default PropositionDetail;
