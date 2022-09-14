import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import SearchButton from "@/components/search/SearchButton";
import TodayInHistory, { TodayInHistoryProps } from "@/components/TodayInHistory";
import { SerpModule } from "@/types/modules";
import CloseIcon from "@mui/icons-material/Close";
import { Box, Button, CardHeader, Divider, Grid, Link } from "@mui/material";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import { styled } from "@mui/material/styles";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { SxProps } from "@mui/system";
import axios from "axios";
import { GetStaticProps } from "next";
import { useRouter } from "next/router";
import { FC, MouseEventHandler, ReactNode, useRef } from "react";

const StyledCard = styled(Card)({
  padding: "1rem",
  height: "100%",
});

const StyledCardHeader: FC<{ title: string }> = ({ title }) => (
  <CardHeader
    title={title}
    titleTypographyProps={{
      variant: "h6",
      gutterBottom: true,
      fontWeight: "bold",
      style: { textAlign: "center" },
    }}
  />
);

interface GridItemProps {
  children: ReactNode;
  sx?: SxProps;
}

interface HomePageProps {
  featuredModules: SerpModule[];
  todayInHistoryModules: SerpModule[];
}

const GridItem: FC<GridItemProps> = ({ children, sx }: GridItemProps) => (
  <Grid item md={12} lg={"auto"} alignItems="center" justifyContent="center" sx={sx}>
    {children}
  </Grid>
);

const Home: FC<HomePageProps> = ({ todayInHistoryModules, featuredModules }: HomePageProps) => {
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
      <Grid container justifyContent="center" spacing={{ xs: 2, md: 3, lg: 4 }} sx={{ p: 4 }}>
        <GridItem>
          <StyledCard raised sx={{ maxWidth: { lg: "50rem" } }}>
            <StyledCardHeader title="About ModularHistory" />
            <CardContent>
              <AboutModularHistory />
            </CardContent>
          </StyledCard>
        </GridItem>
        <GridItem>
          <StyledCard raised>
            <StyledCardHeader title="Module Search" />
            <CardContent>
              <p style={{ textAlign: "center" }}>Search modules by topic, entity, or keywords.</p>
              {searchForm}
            </CardContent>
          </StyledCard>
        </GridItem>
        {featuredModules.length > 0 && (
          <GridItem>
            <StyledCard raised>
              <StyledCardHeader title="Featured Content" />
              <CardContent>
                <FeaturedContent modules={featuredModules} />
              </CardContent>
            </StyledCard>
          </GridItem>
        )}
        {todayInHistoryModules.length > 0 && (
          <GridItem>
            <StyledCard raised sx={{ minWidth: "20rem" }}>
              <StyledCardHeader title="Today in History" />
              <CardContent>
                <TodayInHistory modules={todayInHistoryModules} />
              </CardContent>
            </StyledCard>
          </GridItem>
        )}
        <GridItem>
          <StyledCard raised hidden>
            <CardContent>
              <SubscriptionBox />
            </CardContent>
          </StyledCard>
        </GridItem>
      </Grid>
    </Layout>
  );
};

export default Home;

const AboutModularHistory: FC = () => {
  return (
    <>
      <p style={{ padding: "0 2rem" }}>
        ModularHistory is a nonprofit organization dedicated to helping people learn about and
        understand the history of current issues of sociopolitical discourse.
      </p>
      <p style={{ textAlign: "center" }}>
        <Button variant="contained" href="/about">
          Learn More
        </Button>
      </p>
      <Divider variant="middle" />
      <p style={{ textAlign: "center", paddingTop: "1rem" }}>
        To support ModularHistory’s mission, you can{" "}
        <Link href="/about/contributing">{"contribute content"}</Link> and/or{" "}
        <Link href="/donations">{"donate"}</Link>.
      </p>
    </>
  );
};

interface FeaturedContentProps {
  modules: SerpModule[];
}

const FeaturedContent: FC<FeaturedContentProps> = ({ modules }: FeaturedContentProps) => {
  return (
    <Grid container alignItems="center" justifyContent="center">
      {modules.length ? (
        modules.map((module, index) => (
          <Grid item key={index} xs={12} sm={6} md={4} lg={3}>
            <Link href={module.absoluteUrl} underline="none">
              <a>
                <ModuleUnionCard module={module} />
              </a>
            </Link>
          </Grid>
        ))
      ) : (
        <p>Sorry, there is no featured content to display. Please check back later!</p>
      )}
    </Grid>
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
  );

  return (
    <StyledCard raised>
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

export const getStaticProps: GetStaticProps = async () => {
  let todayInHistoryModules: TodayInHistoryProps[] = [];
  let featuredModules: FeaturedContentProps[] = [];

  const tihPromise = axios
    .get(`http://${process.env.DJANGO_HOST}:${process.env.DJANGO_PORT}/api/home/today_in_history/`)
    .then((response) => {
      todayInHistoryModules = response.data;
    });

  const featuredPromise = axios
    .get(`http://${process.env.DJANGO_HOST}:${process.env.DJANGO_PORT}/api/home/features/`)
    .then((response) => {
      featuredModules = response.data;
    });

  await Promise.allSettled([tihPromise, featuredPromise]);

  return {
    props: { todayInHistoryModules, featuredModules },
    revalidate: 10,
  };
};
