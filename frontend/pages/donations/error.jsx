import Layout from "@/components/Layout";
import { Button } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { makeStyles } from "@material-ui/core/styles";
import React from "react";

const useStyles = makeStyles({
  root: {
    height: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginTop: "1.5rem",
    marginBottom: "2rem",
  },
});

export default function Error() {
  const classes = useStyles();
  return (
    <Layout title="Error">
      <Container>
        <div className={classes.root}>
          <div className="pt-5">
            <p className="h1 mt-5">Oops, something went wrong.</p>
            <div className="mt-3 pt-5 h4">Sorry, there were some issues with your donation.</div>
          </div>
        </div>
      </Container>
    </Layout>
  );
}
