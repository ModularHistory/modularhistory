import Layout from "@/components/Layout";
import SearchButton from "@/components/search/SearchButton";
import { Box } from "@mui/material";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import TextField from "@mui/material/TextField";
import { useRouter } from "next/router";
import { MouseEventHandler, useRef } from "react";

export default function Home() {
  const router = useRouter();
  const queryInputRef = useRef<HTMLInputElement>(null);

  // event handler for pressing enter or clicking search button
  const search = ({ key }: { key?: string }) => {
    if (key && key !== "Enter") return;
    router.push({
      pathname: "/search/",
      query: { query: queryInputRef.current?.value },
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
          inputRef={queryInputRef}
          id={"id_query"}
          name={"query"}
          variant={"outlined"}
          size={"small"}
          style={{ minWidth: "280px" }}
          onKeyPress={search}
          inputProps={{ "data-testid": "query" }}
        />
      </Grid>
      <Grid item>
        <SearchButton onClick={search as MouseEventHandler} data-testid={"searchButton"} />
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
