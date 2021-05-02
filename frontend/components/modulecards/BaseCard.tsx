import { BaseModule } from "@/interfaces";
import { Card } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { ReactNode } from "react";

const useStyles = makeStyles({
  card: {
    quotes: '"“" "”" "‘" "’"',
    cursor: "pointer",
    position: "relative",
    textOverflow: "ellipsis",
    minHeight: "15rem",
    color: "black",
    "&:first-child": {
      marginTop: "0 !important",
    },
    "& .fa": {
      "-webkit-text-stroke": "initial",
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
      width: "100%",
      height: "100%",
      opacity: "0.6",
      backgroundColor: "black",
      backgroundPosition: "center",
      backgroundRepeat: "no-repeat",
      backgroundSize: "100% auto",
      "&:hover": {
        opacity: "0.7",
      },
    },
  },
  cardHeader: {
    margin: 0,
    position: "relative",
    left: 0,
    right: 0,
    zIndex: 1,
    display: "block",
    backgroundImage: "linear-gradient(black, rgba(0,0,0,0.8), rgba(0,0,0,0.8), rgba(0,0,0,0))",
    paddingBottom: "0.2rem",
    color: "white",
    "-webkit-text-stroke": "1px white",
  },
  cardBody: {
    backgroundImage: "linear-gradient(rgba(0,0,0,0), rgba(0,0,0,0.8), rgba(0,0,0,0.8), black)",
    color: "white",
    position: "absolute",
    left: 0,
    right: 0,
    bottom: 0,
    fontSize: "0.8rem",
    "-webkit-text-stroke": "1px white",
    textAlign: "center",
    "&:last-child": {
      padding: "0.5rem",
      paddingBottom: "0.3rem",
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
    // }
  },
});

interface ModuleCardProps {
  module: BaseModule;
  content: any;
  children?: ReactNode;
}

export default function BaseCard({ module, content, children }: ModuleCardProps) {
  const classes = useStyles();
  const isImage = module["model"] === "images.Image";
  let bgImage;
  if (!isImage) {
    bgImage = module["serialized_images"]?.[0];
  }
  return (
    <Card className={`m-2 ${classes.card}`}>
      {false && process.env.ENVIRONMENT != "prod" && !module["verified"] && (
        <span style={{ display: "inline-block", position: "absolute", top: "1px", right: "1px" }}>
          UNVERIFIED
        </span>
      )}
      {bgImage && (
        <div
          className="img-bg lazy-bg"
          data-img={bgImage["src_url"]}
          style={{
            backgroundPosition: bgImage["bg_img_position"],
            backgroundImage: `url(${bgImage["src_url"]})`,
          }}
        />
      )}
      {!isImage && module["dateHtml"] && (
        <p className={`text-center ${classes.cardHeader}`}>
          <small dangerouslySetInnerHTML={{ __html: module["dateHtml"] }} />
        </p>
      )}
      {content && <div className={classes.cardBody}>{content}</div>}
      {children}
    </Card>
  );
}
