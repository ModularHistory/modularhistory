import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Container from "@material-ui/core/Container";
import axios from "axios";
import { GetStaticProps } from "next";
import { FC } from "react";

interface FlatPageProps {
  content: string;
}

const AboutPage: FC<FlatPageProps> = ({ content }: FlatPageProps) => {
  return (
    <Layout title={"About"}>
      <Container>
        <PageHeader>About</PageHeader>
        <div dangerouslySetInnerHTML={{ __html: content }} />
      </Container>
    </Layout>
  );
};

export default AboutPage;

export const getStaticProps: GetStaticProps = async () => {
  let content;
  let notFound = false;
  await axios
    .get(`http://django:8000/api/flatpages//about/`)
    .then((response) => {
      content = response.data.content;
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
      content,
    },
    notFound,
    revalidate: 10,
  };
};
