import Layout from "../components/layout";
import Link from "next/link";

import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";

import {useCallback, useState} from "react";
import {useRouter} from "next/router";
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

function useQueryState(...args) {
  const [query, setQuery] = useState(...args);
  return [query, ({target: {value}}) => setQuery(value)];
}

export default function Home() {
  // TODO: show loading state during transition to search page

  const classes = useStyles();
  const router = useRouter();
  const [query, setQuery] = useQueryState("");

  const search = useCallback(({key}) => {
    if (key !== "Enter") return;
    router.push({
      pathname: "/search/",
      query: {query}
    });
  }, [router]);

  const searchForm = (
    <Grid
      container direction={"column"} spacing={2}
      alignItems={"center"} justify={"center"}
    >
      <Grid item>
        <TextField
          id={"id_query"} name={"query"} variant={"outlined"}
          size={"small"} style={{minWidth: "280px"}}
          onChange={setQuery} onKeyPress={search}
        />
      </Grid>
      <Grid item>
        <Link href={`/search/?query=${query}`} passHref>
          <Button variant={"contained"} color={"primary"}
                  size={"large"} component={'a'}
          >
            Search
          </Button>
        </Link>
      </Grid>
    </Grid>
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
