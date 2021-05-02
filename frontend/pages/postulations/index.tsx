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

interface PostulationsProps {
  postulationsData: any;
}

const Postulations: FC<PostulationsProps> = ({ postulationsData }: PostulationsProps) => {
  const postulations = postulationsData["results"] || [];
  const postulationCards = postulations.map((postulation) => (
    <Grid item key={postulation["slug"]} xs={6} sm={4} md={3}>
      <Link href={`/postulations/${postulation["slug"]}`}>
        <a>
          <BaseCard module={postulation} content={postulation["summary"]} />
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout title={"Postulations"}>
      <Container>
        <PageHeader>Postulations</PageHeader>
        <Pagination count={postulationsData["total_pages"]} />
        <Grid container spacing={2}>
          {postulationCards}
        </Grid>
        <Pagination count={postulationsData["total_pages"]} />
      </Container>
    </Layout>
  );
};

export default Postulations;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let postulationsData = {};

  await axiosWithoutAuth
    .get("http://django:8000/api/postulations/", { params: context.query })
    .then((response) => {
      postulationsData = response.data;
    })
    .catch((error) => {
      // console.error(error);
    });

  return {
    props: {
      postulationsData,
    },
  };
};
