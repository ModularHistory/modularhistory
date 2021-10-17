import Layout from "@/components/Layout";
import SearchButton from "@/components/search/SearchButton";
import { Box } from "@material-ui/core";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import { useRouter } from "next/router";
import { MouseEventHandler, useState } from "react";

function useQueryState(initialState: string) {
  const [query, setQuery] = useState(initialState);
  const setQueryFromEvent = ({ target: { value } }: { target: { value: string } }) =>
    setQuery(value);
  return [query, setQueryFromEvent] as const;
}

export default function Home() {
  const router = useRouter();
  const [query, setQuery] = useQueryState("");

  // event handler for pressing enter or clicking search button
  const search = ({ key }: { key?: string }) => {
    if (key && key !== "Enter") return;
    router.push({
      pathname: "/search/",
      query: { query },
    });
  };

  const searchForm = (
    <Grid
      container
      direction={"column"}
      spacing={2}
      alignItems={"center"}
      justifyContent={"center"}
    >
      <Grid item>
        <TextField
          id={"id_query"}
          name={"query"}
          variant={"outlined"}
          size={"small"}
          style={{ minWidth: "280px" }}
          onChange={setQuery}
          onKeyPress={search}
          data-cy={"query"}
        />
      </Grid>
      <Grid item>
        <SearchButton onClick={search as MouseEventHandler} data-cy={"searchButton"} />
      </Grid>
    </Grid>
  );

  return (
    <Layout title={"Home"}>
      <Box
        sx={{
          flex: "1 1",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          margin: "1.5rem 1rem 1.5rem 1rem",
        }}
      >
        <Card elevation={5}>
          <CardContent>
            <Container>
              <p>Search modules by topic, entity, or keywords.</p>
              {searchForm}
            </Container>
          </CardContent>
        </Card>
      </Box>
    </Layout>
  );
}