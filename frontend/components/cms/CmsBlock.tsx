import { ModuleUnion } from "@/interfaces";
import { Grid } from "@material-ui/core";
import Button from "@material-ui/core/Button";
import { makeStyles } from "@material-ui/styles";
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
      {(!!module.pullRequests?.length && (
        <div>
          {module.pullRequests.map((pullRequest) => (
            <p key={pullRequest.url}>{pullRequest.url}</p>
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
                <Button variant="contained" onClick={openChangePage}>
                  Submit a change for review
                </Button>
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
                <Button variant="contained" onClick={openIssuePage}>
                  Report an issue
                </Button>
              </p>
            </div>
          </Grid>
        </Grid>
      )}
    </>
  );
};

export default CmsBlock;
