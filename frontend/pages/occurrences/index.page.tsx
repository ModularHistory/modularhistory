import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import { Occurrence } from "@/types/modules";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import Link from "next/link";
import { FC } from "react";

interface OccurrencesProps {
  occurrencesData: {
    results: Occurrence[];
    totalPages: number;
  };
}

const Occurrences: FC<OccurrencesProps> = ({ occurrencesData }: OccurrencesProps) => {
  const occurrences = occurrencesData["results"] || [];
  const occurrenceCards = occurrences.map((occurrence) => (
    <Grid item key={occurrence.slug} xs={6} sm={4} md={3}>
      <Link href={`/occurrences/${occurrence.slug}`} prefetch={false}>
        <a>
          <ModuleUnionCard module={occurrence} />
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout>
      <NextSeo
        title={"Occurrences"}
        canonical={"/occurrences"}
        description={
          "Browse historical occurrences related to your topics or entities of interest."
        }
      />
      <Container>
        <PageHeader>Occurrences</PageHeader>
        <Pagination count={occurrencesData["totalPages"]} />
        <Grid container spacing={2}>
          {occurrenceCards}
        </Grid>
        <Pagination count={occurrencesData["totalPages"]} />
      </Container>
    </Layout>
  );
};

export default Occurrences;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let occurrencesData = {};

  await axiosWithoutAuth
    .get("http://django:8002/api/occurrences/", { params: context.query })
    .then((response) => {
      occurrencesData = response.data;
    });

  return {
    props: {
      occurrencesData,
    },
  };
};
