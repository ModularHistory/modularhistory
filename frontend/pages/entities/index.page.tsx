import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import { Entity } from "@/types/modules";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { FC } from "react";

interface EntitiesDataProps {
  totalPages: number;
  results: Entity[];
}

interface EntitiesProps {
  entitiesData: EntitiesDataProps;
}

const Entities: FC<EntitiesProps> = ({ entitiesData }: EntitiesProps) => {
  const entities = entitiesData.results || [];
  const entityCards = entities.map((entity) => (
    <Grid item key={entity.slug} xs={6} sm={4} md={3}>
      <Link href={`/entities/${entity.slug}`} prefetch={false}>
        <a>
          <ModuleUnionCard module={entity} />
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout title={"Entities"}>
      <Container>
        <PageHeader>Entities</PageHeader>
        <Pagination count={entitiesData["totalPages"]} />
        <Grid container spacing={2}>
          {entityCards}
        </Grid>
        <Pagination count={entitiesData["totalPages"]} />
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
    });

  return {
    props: {
      entitiesData,
    },
  };
};
