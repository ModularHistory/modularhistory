import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import CardHeader from "@material-ui/core/CardHeader";
import CardMedia from "@material-ui/core/CardMedia";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import { useTheme } from "@material-ui/core/styles";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import Pagination from "@material-ui/lab/Pagination";
import PaginationItem from "@material-ui/lab/PaginationItem";
import axios from "axios";
import Link from "next/link";
import { useRouter } from "next/router";
import React, { forwardRef, useState } from "react";
import Layout from "../../components/Layout";

const PaginationLink = forwardRef(({ href, ...childProps }, ref) => (
  <Link href={href}>
    <a ref={ref} {...childProps} />
  </Link>
));

function usePageState(...args) {
  const [state, setState] = useState(...args);
  return [state, (e) => setState(Number(e.target.dataset.index))];
}

// TODO: convert to generic version
function EntitiesPagination({ count, ...childProps }) {
  // TODO: integrate route events to make page selection responsive
  //       https://nextjs.org/docs/api-reference/next/router#routerevents
  const router = useRouter();
  const theme = useTheme();

  const sibCount =
    1 +
    ["sm", "md"]
      .map((size) => useMediaQuery(theme.breakpoints.up(size)))
      .reduce((sum, current) => sum + current);

  const [pageNum, setPageNum] = usePageState(Number(router.query["page"] || 1));

  return (
    <Pagination
      count={count}
      page={pageNum}
      siblingCount={sibCount}
      onChange={setPageNum}
      variant="outlined"
      shape="rounded"
      size={sibCount > 2 ? "large" : undefined}
      renderItem={(item) => (
        <PaginationItem
          {...item}
          component={PaginationLink}
          data-index={item.page}
          href={item.page > 1 ? `/entities?page=${item.page}` : router.pathname}
        />
      )}
      {...childProps}
    />
  );
}

export default function Entities({ entitiesData }) {
  const entities = entitiesData["results"] || [];

  const entityCards = entities.map((entity) => (
    <Grid item key={entity["pk"]} xs={6} sm={4} md={3}>
      <a href={`entities/${entity["pk"]}`}>
        <Card>
          <CardHeader title={entity["name"]} />
          {entity["serialized_images"].length > 0 && (
            <CardMedia
              style={{ height: 0, paddingTop: "100%" }}
              image={entity["serialized_images"][0]["src_url"]}
            />
          )}
          <CardContent dangerouslySetInnerHTML={{ __html: entity["description"] }} />
        </Card>
      </a>
    </Grid>
  ));

  return (
    <Layout title={"Entities"}>
      <Container>
        <EntitiesPagination count={entitiesData["total_pages"]} />
        <Grid container spacing={2}>
          {entityCards}
        </Grid>
      </Container>
      {/*<pre>{JSON.stringify(entitiesData, null, 4)}</pre>*/}
    </Layout>
  );
}

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export async function getServerSideProps(context) {
  const q = context.query;
  let entitiesData = {};

  await axios
    .get("http://django:8000/api/entities/" + ("page" in q ? `?page=${q["page"]}` : ""))
    .then((response) => {
      entitiesData = response.data;
    })
    .catch((error) => {
      // console.error(error);
    });

  return {
    props: {
      entitiesData,
    },
  };
}
