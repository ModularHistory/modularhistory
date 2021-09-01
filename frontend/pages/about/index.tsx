import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Container from "@material-ui/core/Container";
import axios from "axios";
import { GetStaticProps } from "next";
import { FC } from "react";
import { FlatPageProps } from "../[path]";

const AboutPage: FC<FlatPageProps> = ({ page }: FlatPageProps) => {
  return (
    <Layout title={"About"}>
      <Container>
        <PageHeader>About</PageHeader>
        <div dangerouslySetInnerHTML={{ __html: page.content }} />
      </Container>
    </Layout>
  );
};

export default AboutPage;

export const getStaticProps: GetStaticProps = async () => {
  let page;
  let notFound = false;
  await axios
    .get(`http://django:8000/api/flatpages//about/`)
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
