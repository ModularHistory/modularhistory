import Layout from "../components/Layout";
import Link from "next/link";

import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";

import {useEffect, useState} from "react";
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
  }
})

function useQueryState(...args) {
  const [query, setQuery] = useState(...args);
  return [query, ({target: {value}}) => setQuery(value)];
}

export default function Home() {
  const classes = useStyles();
  const router = useRouter();
  const [query, setQuery] = useQueryState("");
  const [isLoading, setLoading] = useState(false);

  // NextJS router event subscriptions as a placeholder
  // for a more complex loading indicator
  // https://nextjs.org/docs/api-reference/next/router
  // https://github.com/vercel/next.js/blob/canary/docs/api-reference/next/router.md
  useEffect(() => {
    const handleRouteChangeStart = () => setLoading(true);
    const handleRouteChangeComplete = () => setLoading(false);
    const handleRouteChangeError = () => setLoading(false);
    router.events.on("routeChangeStart", handleRouteChangeStart);
    router.events.on("routeChangeComplete", handleRouteChangeComplete);
    router.events.on("routeChangeError", handleRouteChangeError);
    return () => {
      router.events.off("routeChangeStart", handleRouteChangeStart);
      router.events.off("routeChangeComplete", handleRouteChangeComplete);
      router.events.off("routeChangeError", handleRouteChangeError);
    }
  }, []);

  const search = ({key}) => {
    if (key && key !== "Enter") return;
    router.push({
      pathname: "/search/",
      query: {query}
    });
  };

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
        <Button variant={"contained"} color={"primary"}
                size={"large"} onClick={search} disabled={isLoading}
        >
          {isLoading ? "Loading" : "Search"}
        </Button>
      </Grid>
    </Grid>
  );

  return (
    <Layout title={"Home"}>
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
