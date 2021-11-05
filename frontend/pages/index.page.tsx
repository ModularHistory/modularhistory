import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import SearchButton from "@/components/search/SearchButton";
import TodayInHistory from "@/components/TodayInHistory";
import { ModuleUnion, Topic } from "@/types/modules";
import CloseIcon from "@mui/icons-material/Close";
import { Box, Button, Divider, Grid, Link, Skeleton } from "@mui/material";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import { styled } from "@mui/material/styles";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import axios from "axios";
import { useRouter } from "next/router";
import { FC, MouseEventHandler, useEffect, useRef, useState } from "react";

const StyledCard = styled(Card)({
  padding: "1rem",
  height: "100%",
});

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
      <Grid container spacing={{ xs: 2, md: 3, lg: 4 }} sx={{ p: 4 }}>
        <Grid item md={12} lg={"auto"} alignItems="center" justifyContent="center">
          <StyledCard elevation={5}>
            <AboutModularHistory />
          </StyledCard>
        </Grid>
        <Grid item md={12} lg={"auto"}>
          <StyledCard elevation={5}>
            <CardContent>
              <p style={{ textAlign: "center" }}>Search modules by topic, entity, or keywords.</p>
              {searchForm}
            </CardContent>
          </StyledCard>
        </Grid>
        <Grid item md={12} lg={"auto"} alignItems="center" justifyContent="center">
          <StyledCard elevation={5}>
            <FeaturedContent />
          </StyledCard>
        </Grid>
        <Grid item md={12} lg={"auto"} alignItems="center" justifyContent="center">
          <StyledCard elevation={5}>
            <TodayInHistory />
          </StyledCard>
        </Grid>
        <Grid item md={12} lg={"auto"} alignItems="center" justifyContent="center" hidden>
          <StyledCard elevation={5}>
            <SubscriptionBox />
          </StyledCard>
        </Grid>
      </Grid>
    </Layout>
  );
}

const AboutModularHistory: FC = () => {
  return (
    <Box>
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
              <Link href="/about/contributing">{"contribute content"}</Link> and/or{" "}
              <Link href="/donations">{"donate"}</Link>.
            </p>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

const FeaturedContent: FC = () => {
  const [items, setItems] = useState<Exclude<ModuleUnion, Topic>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cancelTokenSource = axios.CancelToken.source();
    axiosWithoutAuth
      .get("/api/home/features/", { cancelToken: cancelTokenSource.token })
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
    <Box>
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
                <Grid item key={index} xs={12} sm={6} md={4} lg={3} xl={3}>
                  <Link href={module.absoluteUrl} underline="none">
                    <a>
                      <ModuleUnionCard module={module} />
                    </a>
                  </Link>
                </Grid>
              ))
            ) : loading ? (
              <Grid item xs={12} sm={6} md={4} lg={3} xl={3}>
                <StyledCard>
                  <CardContent>
                    <Skeleton sx={{ minHeight: 200, width: "100%" }} />
                  </CardContent>
                </StyledCard>
              </Grid>
            ) : (
              <p>Sorry, there are no featured contents to display. Please check back later!</p>
            )}
          </>
        </Grid>
      </Box>
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
    <StyledCard elevation={5}>
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
    </StyledCard>
  );
};
