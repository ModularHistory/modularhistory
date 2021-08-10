import { ModuleUnion } from "@/interfaces";
import { Grid } from "@material-ui/core";
import Button from "@material-ui/core/Button";
import { makeStyles } from "@material-ui/styles";
import Link from "next/link";
import { useRouter } from "next/router";
import { FC } from "react";

const useStyles = makeStyles({
  root: {},
});

interface CmsBlockProps {
  module: ModuleUnion;
}

const CmsBlock: FC<CmsBlockProps> = ({ module }: CmsBlockProps) => {
  const classes = useStyles();
  const router = useRouter();
  const openIssuePage = () => {
    console.log();
  };
  const openChangePage = () => {
    console.log(module.absoluteUrl);
    router.push(`${module.absoluteUrl}/modify`);
  };
  return (
    <>
      {(!!module.changes?.length && (
        <div>
          {module.changes.map((change) => (
            <p key={change.url}>{change.url}</p>
          ))}
        </div>
      )) || (
        <Grid item container xs={12} justifyContent="center">
          <Grid item xs={12} sm={6}>
            <div
              style={{
                margin: "2rem",
                borderTop: "1px solid gray",
                textAlign: "center",
                paddingTop: "1.5rem",
              }}
            >
              <p>No changes are under review for this module.</p>
              <p>
                <Link href={`${module.absoluteUrl}modify`}>
                  <a>
                    <Button variant="contained">Submit a change for review</Button>
                  </a>
                </Link>
              </p>
            </div>
          </Grid>
        </Grid>
      )}
      {(!!module.issues?.length && (
        <div>
          {module.issues.map((issue) => (
            <p key={issue.url}>{issue.url}</p>
          ))}
        </div>
      )) || (
        <Grid item container xs={12} justifyContent="center">
          <Grid item xs={12} sm={6}>
            <div
              style={{
                margin: "2rem",
                borderTop: "1px solid gray",
                textAlign: "center",
                paddingTop: "1.5rem",
              }}
            >
              <p>No issues have been reported for this module.</p>
              <p>
                <Link href="/">
                  <a>
                    <Button variant="contained">Report an issue</Button>
                  </a>
                </Link>
              </p>
            </div>
          </Grid>
        </Grid>
      )}
    </>
  );
};

export default CmsBlock;
