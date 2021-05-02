import axiosWithoutAuth from "@/axiosWithoutAuth";
import ImageCard from "@/components/cards/ImageCard";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { FC } from "react";

interface ImagesProps {
  imagesData: any;
}

const Images: FC<ImagesProps> = ({ imagesData }: ImagesProps) => {
  const images = imagesData["results"] || [];
  const imageCards = images.map((image) => (
    <Grid item key={image["slug"] || image["pk"]} xs={6} sm={4} md={3}>
      <Link href={`/images/${image["slug"] || image["pk"]}`}>
        <a>
          <ImageCard image={image} />
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout title={"Images"}>
      <Container>
        <PageHeader>Images</PageHeader>
        <Pagination count={imagesData["total_pages"]} />
        <Grid container spacing={2}>
          {imageCards}
        </Grid>
        <Pagination count={imagesData["total_pages"]} />
      </Container>
    </Layout>
  );
};

export default Images;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let imagesData = {};

  await axiosWithoutAuth
    .get("http://django:8000/api/images/", { params: context.query })
    .then((response) => {
      imagesData = response.data;
    })
    .catch((error) => {
      // console.error(error);
    });

  return {
    props: {
      imagesData,
    },
  };
};
