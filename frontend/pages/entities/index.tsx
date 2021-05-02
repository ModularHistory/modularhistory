import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import BaseCard from "@/components/modulecards/BaseCard";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { FC } from "react";

interface EntitiesProps {
  entitiesData: any;
}

const Entities: FC<EntitiesProps> = ({ entitiesData }: EntitiesProps) => {
  const entities = entitiesData["results"] || [];
  const entityCards = entities.map((entity) => (
    <Grid item key={entity["pk"]} xs={6} sm={4} md={3}>
      <Link href={`/entities/${entity["slug"]}`}>
        <a>
          <BaseCard module={entity} content={entity["truncated_description"]} />
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout title={"Entities"}>
      <Container>
        <PageHeader>Entities</PageHeader>
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
