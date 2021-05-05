import Layout from "@/components/Layout";
import { StaticPage as StaticPageType } from "@/interfaces";
import { Container, useMediaQuery } from "@material-ui/core";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

interface StaticPageProps {
  page: StaticPageType;
}

const StaticPage: FC<StaticPageProps> = ({ page }: StaticPageProps) => {
  // check if the viewport width is less than 36rem
  const isSmall = useMediaQuery("@media (max-width:36rem)");

  return (
    <Layout title={page.title}>
      <Container style={{ padding: `1.25rem ${isSmall ? "1.25rem" : "5rem"}`, maxWidth: "50rem" }}>
        <h1>{page.title}</h1>
        <div dangerouslySetInnerHTML={{ __html: page["content"] }} />
      </Container>
    </Layout>
  );
};
export default StaticPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let page = {};
  const { path } = params;

  await axios
    // the "extra" slashes around `path` are currently needed to
    // match the `url` attribute of the StaticPage model.
    .get(`http://django:8000/api/staticpages//${path}/`)
    .then((response) => {
      page = response.data;
    })
    .catch((error) => {
      // TODO: how should we handle errors here?
    });

  return {
    props: {
      page,
    },
    revalidate: 10,
  };
};

export const getStaticPaths: GetStaticPaths = async () => {
  return {
    paths: [],
    fallback: "blocking",
  };
};
