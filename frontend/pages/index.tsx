import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import SearchButton from "@/components/search/SearchButton";
import { Box, Container, Divider, Grid, Link, Paper } from "@mui/material";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import TextField from "@mui/material/TextField";
import { useRouter } from "next/router";
import { FC, MouseEventHandler, useState } from "react";

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
      <AboutModularHistory />
    </Layout>
  );
}

const AboutModularHistory: FC  = () => {
  return(
    <Container sx={{marginBottom: "20px"}}>
      <PageHeader>About Modularhistory</PageHeader>
      <Paper sx={{p: 2, margin: "0 auto", maxWidth: "80vw", flexGrow: 1}}>
        <Grid container spacing = {2}>
          <Grid item xs>
            <p>ModularHistory is a 501(c)(3) nonprofit organization dedicated to helping people learn about and understand the history of our world, our society, and issues of modern sociopolitical discourse.</p>
            <Divider variant = "middle" />
            <p>ModularHistory provide its content for free.</p>
            <p>To support us, <Link href = "/donations" variant = "body2">{' donate now.'}</Link></p>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};