import Head from "next/head";
// import styles from "../styles/Home.module.css";
import Layout from "../components/layout";

import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";

import {makeStyles} from "@material-ui/core/styles";

const useStyles = makeStyles({
  root: {
    position: "relative",
    height: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginTop: "1.5rem",
    // backgroundImage: url('{% static "topic_cloud.png" %}'),
    backgroundRepeat: "no-repeat",
    backgroundPosition: "center",
    backgroundSize: "contain",
  }
})

export default function Home() {
  const classes = useStyles();

  const searchForm = (
    <form action={"/search"} method={"get"} id={"search-form"}>
      <Grid
        container direction={"column"} spacing={2}
        alignItems={"center"} justify={"center"}
      >
        <Grid item>
          <TextField
            id={"id_query"} name={"query"} variant={"outlined"}
            size={"small"} style={{minWidth: "280px"}}/>
        </Grid>
        <Grid item>
          <Button variant={"contained"} color={"primary"}
                  size={"large"} type={"submit"}>
            Search
          </Button>
        </Grid>
      </Grid>
    </form>
  );

  return (
    <Layout>
      <div className={classes.root}>
        <Card elevation={5}>
          <CardContent>
            <Container>
              <p>Search modules by topic, entity, or keywords.</p>
              {searchForm}
            </Container>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
