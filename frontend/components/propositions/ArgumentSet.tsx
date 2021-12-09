import { Argument } from "@/types/models";
import { TreeItem, TreeView } from "@mui/lab";
import { TreeItemProps } from "@mui/lab/TreeItem";
import { alpha, Theme } from "@mui/material";
import Collapse from "@mui/material/Collapse";
import SvgIcon, { SvgIconProps } from "@mui/material/SvgIcon";
import { TransitionProps } from "@mui/material/transitions";
import { createStyles, withStyles } from "@mui/styles";
import { animated, useSpring } from "@react-spring/web";
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

interface ArgumentSetProps {
  argumentSet: Argument[];
}

const ArgumentSet: FC<ArgumentSetProps> = ({ argumentSet }: ArgumentSetProps) => {
  const filteredArguments = argumentSet.filter(
    (argument) => argument.explanation && !!argument.premises?.length
  );
  return (
    <TreeView
      defaultExpanded={filteredArguments.map((argument) => `${argument.id}`)}
      defaultCollapseIcon={<MinusSquare />}
      defaultExpandIcon={<PlusSquare />}
      defaultEndIcon={<CloseSquare />}
      sx={{
        marginBottom: "1.5rem",
        flexGrow: 1,
      }}
    >
      {filteredArguments.map((argument, index) => (
        <StyledTreeItem
          key={argument.id}
          nodeId={`${argument.id}`}
          label={
            <span
              dangerouslySetInnerHTML={{ __html: argument.explanation || `Argument ${index + 1}` }}
            />
          }
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
  );
};

export default ArgumentSet;
