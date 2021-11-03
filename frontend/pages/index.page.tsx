import DyanmicForm from "@/components/forms/DynamicForm";
import Layout from "@/components/Layout";
import SearchButton from "@/components/search/SearchButton";
import { Box, Button, Container, Divider, Grid, Link } from "@mui/material";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useRouter } from "next/router";
import { FC, MouseEventHandler, useRef } from "react";

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
    <Layout>
      <Grid container spacing={2} columns={16} alignItems={"center"} justifyContent={"center"}>
        <Grid item xs={8} alignItems="center" justifyContent="center">
          <Container>
            <AboutModularHistory />
          </Container>
        </Grid>
        <Grid item xs={8}>
          <Container>
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
            <DyanmicForm />
          </Container>
        </Grid>
      </Grid>
    </Layout>
  );
}

const AboutModularHistory: FC = () => {
  return (
    <Box
      sx={{
        flex: "1 1",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        margin: "1.5rem 1rem 1.5rem 1rem",
        p: 4,
      }}
    >
      <Card elevation={5}>
        <Box sx={{ m: 3 }}>
          <Grid container alignItems="center" justifyContent="center">
            <Grid item>
              <Typography variant="h6" gutterBottom component="div" fontWeight="bold">
                About ModularHistory
              </Typography>
            </Grid>
          </Grid>
          <p>
            ModularHistory is a nonprofit organization dedicated to helping people learn about and
            understand the history of our world, our society, and issues of modern sociopolitical
            discourse.
          </p>
          <Button variant="contained" href="/about/">
            Learn More
          </Button>
        </Box>
        <Divider variant="middle" />
        <Box sx={{ m: 3 }}>
          <Grid container alignItems="center">
            <Grid item>
              <p>
                To support ModularHistory’s mission, you can{" "}
                <Link href="/about/contributing" variant="body2">
                  {"contribute content"}
                </Link>{" "}
                and/or{" "}
                <Link href="/donations" variant="body2">
                  {" donate."}
                </Link>
              </p>
            </Grid>
          </Grid>
        </Box>
      </Card>
    </Box>
  );
};
