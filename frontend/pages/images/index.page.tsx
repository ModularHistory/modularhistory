import axiosWithoutAuth from "@/axiosWithoutAuth";
import ImageCard from "@/components/images/ImageCard";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import { Image } from "@/types/modules";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import Link from "next/link";
import { FC } from "react";

interface ImagesProps {
  imagesData: {
    results: Image[];
    totalPages: number;
  };
}

const Images: FC<ImagesProps> = ({ imagesData }: ImagesProps) => {
  const images = imagesData.results || [];
  const imageCards = images.map((image) => (
    <Grid item key={image.pk} xs={6} sm={4} md={3}>
      <Link href={`/images/${image.pk}`}>
        <a>
          <ImageCard image={image} />
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout>
      <NextSeo
        title={"Images"}
        canonical={"/images"}
        description={`Browse images of historical occurrences, places, and entities.`}
      />
      <Container>
        <PageHeader>Images</PageHeader>
        <Pagination count={imagesData.totalPages} />
        <Grid container spacing={2}>
          {imageCards}
        </Grid>
        <Pagination count={imagesData.totalPages} />
      </Container>
    </Layout>
  );
};

export default Images;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let imagesData = {};

  await axiosWithoutAuth
    .get("http://django:8002/api/images/", { params: context.query })
    .then((response) => {
      imagesData = response.data;
    });

  return {
    props: {
      imagesData,
    },
  };
};
