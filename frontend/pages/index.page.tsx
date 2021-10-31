import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import SearchButton from "@/components/search/SearchButton";
import TodayInHistory from "@/components/TodayInHistory";
import { ModuleUnion, Topic } from "@/types/modules";
import { Box, Button, Container, Divider, Grid, Link, Skeleton } from "@mui/material";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import axios from "axios";
import { useRouter } from "next/router";
import React, { FC, MouseEventHandler, useEffect, useRef, useState } from "react";

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
          inputProps={{ "data-testid": "query", "data-cy": "query" }}
        />
      </Grid>
      <Grid item>
        <SearchButton
          onClick={search as MouseEventHandler}
          data-testid={"searchButton"}
          data-cy={"searchButton"}
        />
      </Grid>
    </Grid>
  );

  return (
    <Layout>
      <Grid container spacing={2} sx={{ p: 4 }}>
        <Grid item xs={12}>
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
          </Container>
        </Grid>
        <Grid item xs={12}>
          <Card elevation={5}>
            <CardContent>
              <TodayInHistory />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      <Grid
        container
        spacing={{ xs: 2, md: 3 }}
        columns={{ xs: 12 }}
        alignItems={"center"}
        justifyContent={"center"}
      >
        <Grid item xs={12} sm={6} md={6} alignItems="center" justifyContent="center">
          <Container>
            <AboutModularHistory />
          </Container>
        </Grid>
        <Grid item xs={12} sm={6} md={6}>
          <Container>
            <FeaturedContent />
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
            understand the history of issues of modern sociopolitical discourse.
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

const FeaturedContent: FC = () => {
  const [items, setItems] = useState<Exclude<ModuleUnion, Topic>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axiosWithoutAuth
      .get("/api/home/feature/", { cancelToken: cancelTokenSource.token })
      .then((response) => {
        setItems(response.data);
        setLoading(false);
      })
      .catch((error) => {
        if (axios.isCancel(error)) return;
        console.error(error);
        setLoading(false);
      });
    return () => {
      cancelTokenSource.cancel("component unmounted");
    };
  }, [loading]);

  return (
    <>
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
          <Box sx={{ m: 3, alignItems: "center", justifyContent: "center" }}>
            <Grid container alignItems="center" justifyContent="center">
              <Grid item>
                <Typography variant="h6" gutterBottom component="div" fontWeight="bold">
                  Featured Content
                </Typography>
              </Grid>
            </Grid>
            <Grid container alignItems="center" justifyContent="center">
              <>
                {items.length ? (
                  items.map((module, index) => (
                    <Link href={module.absoluteUrl} underline="none" key={index}>
                      <a>
                        <Grid item>
                          <ModuleUnionCard module={module} key={index} />
                        </Grid>
                      </a>
                    </Link>
                  ))
                ) : loading ? (
                  <Card>
                    <CardContent>
                      <Skeleton sx={{ minHeight: 200 }} />
                    </CardContent>
                  </Card>
                ) : (
                  <p>Sorry, there are no featured contents to display. Please check back later!</p>
                )}
              </>
            </Grid>
          </Box>
        </Card>
      </Box>
    </>
  );
};
