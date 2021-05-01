import axiosWithoutAuth from "@/axiosWithoutAuth";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import CardHeader from "@material-ui/core/CardHeader";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { FC } from "react";
import Layout from "../../components/Layout";
import Pagination from "../../components/Pagination";

interface PostulationsProps {
  postulationsData: any;
}

const Postulations: FC<PostulationsProps> = ({ postulationsData }: PostulationsProps) => {
  const postulations = postulationsData["results"] || [];
  const postulationCards = postulations.map((postulation) => (
    <Grid item key={postulation["slug"]} xs={6} sm={4} md={3}>
      <Link href={`/postulations/${postulation["slug"]}`}>
        <a>
          <Card>
            <CardHeader title={postulation["summary"]} />
            <CardContent dangerouslySetInnerHTML={{ __html: postulation["elaboration"] }} />
          </Card>
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout title={"Postulations"}>
      <Container>
        <Pagination count={postulationsData["total_pages"]} />
        <Grid container spacing={2}>
          {postulationCards}
        </Grid>
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
