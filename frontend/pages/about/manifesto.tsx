import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Container from "@material-ui/core/Container";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";
import { FlatPageProps } from "../[path]";

const Manifesto: FC<FlatPageProps> = ({ page }: FlatPageProps) => {
  return (
    <Layout title={"Manifesto"}>
      <Container>
        <PageHeader>Manifesto</PageHeader>
        <div dangerouslySetInnerHTML={{ __html: page.content }} />
      </Container>
    </Layout>
  );
};

export default Manifesto;

export const getStaticProps: GetStaticProps = async () => {
  let page;
  let notFound = false;
  await axios
    .get(`http://django:8000/api/flatpages//manifesto/`)
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
