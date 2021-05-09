import Layout from "@/components/Layout";
import { Button } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { makeStyles } from "@material-ui/core/styles";
import Link from "next/link";
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
  spacing: {
    marginTop: "2rem",
    marginBottom: "2rem",
  },
});

export default function Success() {
  const classes = useStyles();
  return (
    <Layout title="Success">
      <Container>
        <div className={classes.root}>
          <div className="pt-5">
            <p className="h1 mt-5">Donated Successfully.</p>
            <div className="mt-3 pt-5 h4">
              Thank you for your donation! Your patronage makes ModularHistory possible.
            </div>
            <div className={classes.spacing}>
              <Link href={"/home"}>
                <Button variant="contained" color="primary">
                  Return Home
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </Container>
    </Layout>
  );
}
