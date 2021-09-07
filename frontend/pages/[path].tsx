import Layout from "@/components/Layout";
import { FlatPage as FlatPageType } from "@/types/modules";
import { Container, useMediaQuery } from "@material-ui/core";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

export interface FlatPageProps {
  page: FlatPageType;
}

const FlatPage: FC<FlatPageProps> = ({ page }: FlatPageProps) => {
  // check if the viewport width is less than 36rem
  const isSmall = useMediaQuery("@media (max-width:36rem)");

  return (
    <Layout title={page.title}>
      <Container style={{ padding: `1.25rem ${isSmall ? "1.25rem" : "5rem"}`, maxWidth: "50rem" }}>
        <h1>{page.title}</h1>
        <div dangerouslySetInnerHTML={{ __html: page.content }} />
      </Container>
    </Layout>
  );
};
export default FlatPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let page = null;
  let notFound = false;
  const { path } = params || {};

  await axios
    // the "extra" slashes around `path` are currently needed to
    // match the `url` attribute of the FlatPage model.
    .get(`http://django:8000/api/flatpages//${path}/`)
    .then((response) => {
      page = response.data;
    })
    .catch((error) => {
      if (error.response?.status === 404) {
        notFound = true;
      } else {
        throw error;
      }
    });

  return {
    props: {
      page,
    },
    notFound,
    revalidate: 10,
  };
};

export const getStaticPaths: GetStaticPaths = async () => {
  return {
    paths: [],
    fallback: "blocking",
  };
};
