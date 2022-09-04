import { Image, ModuleUnion, Source, Topic } from "@/types/modules";
import { Card, CardProps } from "@mui/material";
import { styled } from "@mui/material/styles";
import { FC, ReactNode } from "react";

const StyledCard = styled(Card)({
  quotes: '"“" "”" "‘" "’"',
  cursor: "pointer",
  position: "relative",
  textOverflow: "ellipsis",
  minHeight: "15rem",
  minWidth: "15rem",
  maxWidth: "30rem",
  color: "black",
  "&:first-of-type": {
    marginTop: "0 !important",
  },
  "& .fa": {
    WebkitTextStroke: "initial",
    textShadow: "none",
  },
  "&.image-card": {
    "& .card-body": {
      "& p": {
        marginBottom: "1rem",
      },
    },
    "& .image-credit": {
      display: "none",
    },
  },
  "& .img-bg": {
    position: "absolute",
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    opacity: "0.8",
    backgroundColor: "black",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
    backgroundSize: "100% auto",
    "&:hover": {
      opacity: "0.9",
    },
  },
});

const CardHeader = styled("p")({
  margin: 0,
  position: "relative",
  left: 0,
  right: 0,
  zIndex: 1,
  display: "block",
  backgroundImage:
    "linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.7), rgba(0,0,0,0.6), rgba(0,0,0,0.5), rgba(0,0,0,0))",
  paddingBottom: "0.2rem",
  color: "white",
  WebkitTextStroke: "1px white",
});

const CardBody = styled("div")({
  backgroundImage:
    "linear-gradient(rgba(0,0,0,0), rgba(0,0,0,0.5), rgba(0,0,0,0.6), rgba(0,0,0,0.7), rgba(0,0,0,0.8))",
  color: "white",
  position: "absolute",
  width: "100%",
  maxHeight: "50%",
  overflow: "hidden",
  textOverflow: "ellipsis",
  left: 0,
  right: 0,
  bottom: 0,
  fontSize: "0.8rem",
  WebkitTextStroke: "1px white",
  textAlign: "center",
  "&:last-child": {
    padding: "0.5rem",
    paddingBottom: "0.3rem",
  },
  "& p:last-child": {
    paddingBottom: "0.3rem",
    marginBottom: 0,
  },
  //   @include safari {
  //     // On Safari, without this override,
  //     // the shadow goes on top of the text and makes it lighter....
  //     text-shadow: 0 0 1px #ffffff, 0 1px 1px #ffffff,
  //       1px 1px 1px #ffffff, 1px 0 1px #ffffff, 0 0 0.5rem #ffffff,
  //       0 1px 0.5rem #ffffff, 1px 1px 0.5rem #ffffff,
  //       1px 0 0.5rem #ffffff, 0 0 1rem #ffffff, 0 1px 1rem #ffffff,
  //       1px 1px 1rem #ffffff, 1px 0 1rem #ffffff;
  //   }
  "& .blockquote": {
    position: "relative",
    marginBottom: 0,
    fontSize: "0.8rem",
    borderLeft: "none",
    padding: "0.2rem 0.2rem 0 0.2rem",
    lineHeight: "1.2rem",
    "&::before": {
      content: "open-quote",
      position: "absolute",
      top: "-0.25rem",
      left: "-0.25rem",
      fontSize: "3rem",
      fontWeight: "bold",
    },
    "&::after": {
      content: "no-close-quote",
      position: "relative",
      bottom: 0,
      right: 0,
      fontSize: "2rem",
    },
    "& p": {
      position: "relative",
      fontSize: "0.8rem",
    },
    "& footer": {
      marginTop: "0.5rem",
      textAlign: "center",
    },
  },
});

export interface ModuleCardProps extends CardProps {
  module: ModuleUnion;
  header?: string;
  children?: ReactNode;
}

const ModuleCard: FC<ModuleCardProps> = ({
  module,
  header,
  children,
  ...muiCardProps
}: ModuleCardProps) => {
  let bgImage: Image | undefined;
  if (module.model == "images.image") {
    bgImage = module as Image;
  } else if (moduleHasPrimaryImage(module)) {
    bgImage = module.primaryImage;
  }
  return (
    <StyledCard data-type={module.model} data-testid={"moduleCard"} {...muiCardProps}>
      {false && process.env.ENVIRONMENT != "prod" && !module.verified && (
        <span style={{ display: "inline-block", position: "absolute", top: "1px", right: "1px" }}>
          UNVERIFIED
        </span>
      )}
      {(bgImage && (
        <div
          className="img-bg lazy-bg"
          data-img={bgImage.srcUrl}
          style={{
            backgroundPosition: bgImage.bgImgPosition,
            backgroundImage: `url(${bgImage.srcUrl})`,
          }}
        />
      )) || (
        // Note: This applies a dark background to the card.
        <div className="img-bg" />
      )}
      {header ? (
        <CardHeader className={"text-center"}>
          <small dangerouslySetInnerHTML={{ __html: header }} />
        </CardHeader>
      ) : (
        <CardHeader className={"text-center"}>
          {module.title && <small>{module.title}</small>}
          {module.title && module.dateString && <br />}
          {module.dateString && <small dangerouslySetInnerHTML={{ __html: module.dateString }} />}
        </CardHeader>
      )}
      {children && <CardBody>{children}</CardBody>}
    </StyledCard>
  );
};
export default ModuleCard;

function moduleHasPrimaryImage(
  module: ModuleUnion
): module is Exclude<ModuleUnion, Source | Topic> {
  const modelsWithoutImages: ModuleUnion["model"][] = ["topics.topic", "sources.source"];
  return !modelsWithoutImages.includes(module.model);
}
