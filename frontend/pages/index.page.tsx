import Layout from "@/components/Layout";
import SearchButton from "@/components/search/SearchButton";
import TodayInHistory from "@/components/TodayInHistory";
import CloseIcon from "@mui/icons-material/Close";
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Divider,
  Grid,
  Link,
  TextField,
  Typography,
} from "@mui/material";
import { useRouter } from "next/router";
import React, { FC, MouseEventHandler, useRef } from "react";

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
          </Container>
        </Grid>
        <Grid item xs={12}>
          <Card elevation={5}>
            <CardContent>
              <TodayInHistory />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <SubscriptionBox />
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
          <Button variant="contained" href="/about">
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

const SubscriptionBox: FC = () => {
  const submitSubscription = () => {
    return;
  };

  const subscriptionForm = (
    <Grid
      container
      direction={"column"}
      spacing={2}
      alignItems={"center"}
      justifyContent={"center"}
      marginTop={"0rem"}
      marginBottom={"1rem"}
    >
      <Grid item>
        <TextField
          id={"id_subscribeEmail"}
          name={"subscribeEmail"}
          variant={"outlined"}
          size={"small"}
          style={{ minWidth: "280px", marginRight: "1rem" }}
          onKeyPress={submitSubscription}
          label={"Email address"}
        />
        <Button variant="contained" sx={{ minHeight: "40px", height: "100%" }}>
          Sign up!
        </Button>
      </Grid>
    </Grid>
  );

  const subscribeDisclaimer = (
    <Grid container>
      <Box sx={{ fontWeight: "100" }}>
        <Typography style={{ fontSize: "10pt" }}>
          {"By entering your details, you are agreeing to ModularHistory's "}
          <Link href="/privacy">
            <a>privacy policy</a>
          </Link>{" "}
          and{" "}
          <Link href="/terms">
            <a>terms of use</a>
          </Link>
          . You can unsubscribe at any time.
        </Typography>
      </Box>
    </Grid>
  );

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        margin: "1.5rem 1rem 1.5rem 1rem",
      }}
      hidden
    >
      <Card elevation={5}>
        <CardContent>
          <Grid
            item
            sx={{
              alignItems: "center",
              display: "flex",
              justifyContent: "space-between",
            }}
          >
            <Typography style={{ fontSize: "20pt", fontWeight: "bold" }}>
              Sign up for the weekly ModularHistory newsletter
            </Typography>
            <Button>
              <CloseIcon />
            </Button>
          </Grid>
          <Typography>Sign up to recieve our newsletter!</Typography>
          {subscriptionForm}
          {subscribeDisclaimer}
        </CardContent>
      </Card>
    </Box>
  );
};
