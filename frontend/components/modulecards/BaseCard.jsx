import { makeStyles } from "@material-ui/styles";

const useStyles = makeStyles({
  card: {
    quotes: '"“" "”" "‘" "’"',
    cursor: "pointer",
    position: "relative",
    textOverflow: "ellipsis",
    minHeight: "15rem",
    color: "black",
    // TODO: delete this if it's unnecessary
    // "&:first-child": {
    //   marginTop: '0 !important'
    // },
    "& .fa": {
      "-webkit-text-stroke": "initial",
      textShadow: "none",
    },
    "& .card-body": {
      fontSize: "0.8rem",
      "-webkit-text-stroke": "1px black",
      textShadow: `0 0 1px #ffffff, 0 1px 1px #ffffff, 1px 1px 1px #ffffff,
        1px 0 1px #ffffff, 0 0 0.5rem #ffffff, 0 1px 0.5rem #ffffff,
        1px 1px 0.5rem #ffffff, 1px 0 0.5rem #ffffff, 0 0 1rem #ffffff,
        0 1px 1rem #ffffff, 1px 1px 1rem #ffffff, 1px 0 1rem #ffffff,
        0 0 2rem #ffffff, 0 1px 2rem #ffffff, 1px 1px 2rem #ffffff,
        1px 0 2rem #ffffff`,
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
    //   .blockquote {
    //     position: relative;
    //     margin-bottom: 0;
    //     font-size: 0.8rem;
    //     border-left: none;
    //     padding: 0.2rem 0.1rem 0 0.3rem;
    //     line-height: 1.2rem;
    //     &::before {
    //       content: open-quote;
    //       position: absolute;
    //       top: -0.25rem;
    //       left: -0.6rem;
    //       font-size: 3rem;
    //       font-weight: bold;
    //     }
    //     &::after {
    //       content: no-close-quote;
    //       position: relative;
    //       bottom: 0;
    //       right: 0;
    //       font-size: 2rem;
    //     }
    //     p {
    //       position: relative;
    //       font-size: 0.8rem;
    //     }
    //     footer {
    //       margin-top: 0.5rem;
    //       text-align: center;
    //     }
    //   }
    // }
    // &.image-card {
    //   .card-body {
    //     p {
    //       margin-bottom: 1rem;
    //     }
    //   }
    //   .image-credit {
    //     display: none;
    //   }
    // }
  },
});

export default function BaseCard({ module, cardClass, cardStyles, top, children }) {
  // BaseCard is extended by module-specific cards.
  // The code is mostly copied from the `_card.html` Django template.
  const classes = useStyles();

  const isImage = module["model"] === "images.Image";
  let bgImage;
  if (!isImage) {
    bgImage = module["serialized_images"]?.[0];
  }

  return (
    <div className={`card m-2 ${cardClass || classes.card || ""}`} style={cardStyles}>
      {process.env.NODE_ENV != "prod" && !module["verified"] && (
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
        ></div>
      )}

      <div className="card-body" style={{ backgroundColor: "transparent", zIndex: "1" }}>
        {!isImage && module["date_html"] && (
          <p className="card-title text-center my-1">
            <small dangerouslySetInnerHTML={{ __html: module["date_html"] }} />
          </p>
        )}

        {children}
      </div>
    </div>
  );
}
