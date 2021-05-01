import axiosWithoutAuth from "@/axiosWithoutAuth";
import EntityCard from "@/components/modulecards/EntityCard";
// import Card from "@material-ui/core/Card";
// import CardContent from "@material-ui/core/CardContent";
// import CardHeader from "@material-ui/core/CardHeader";
// import CardMedia from "@material-ui/core/CardMedia";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { FC } from "react";
import Layout from "../../components/Layout";
import Pagination from "../../components/Pagination";

interface EntitiesProps {
  entitiesData: any;
}

const Entities: FC<EntitiesProps> = ({ entitiesData }: EntitiesProps) => {
  const entities = entitiesData["results"] || [];
  const entityCards = entities.map((entity) => (
    <Grid item key={entity["pk"]} xs={6} sm={4} md={3}>
      <Link href={`/entities/${entity["slug"]}`}>
        <a>
          {/* <Card>
            <CardHeader title={entity["name"]} />
            {entity["serialized_images"].length > 0 && (
              <CardMedia
                style={{ height: 0, paddingTop: "100%" }}
                image={entity["serialized_images"][0]["src_url"]}
              />
            )}
            <CardContent dangerouslySetInnerHTML={{ __html: entity["truncated_description"] }} />
          </Card> */}
          <EntityCard entity={entity} />
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout title={"Entities"}>
      <Container>
        <Pagination count={entitiesData["total_pages"]} />
        <Grid container spacing={2}>
          {entityCards}
        </Grid>
        <Pagination count={entitiesData["total_pages"]} />
      </Container>
    </Layout>
  );
};

export default Entities;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let entitiesData = {};

  await axiosWithoutAuth
    .get("http://django:8000/api/entities/", { params: context.query })
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
};
