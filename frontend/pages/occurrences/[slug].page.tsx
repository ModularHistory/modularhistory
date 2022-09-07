import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { Occurrence } from "@/types/modules";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { NextSeo } from "next-seo";
import { FC } from "react";

interface OccurrenceProps {
  occurrence: Occurrence;
}

/**
 * A page that renders the HTML of a single occurrence.
 */
const OccurrenceDetailPage: FC<OccurrenceProps> = ({ occurrence }: OccurrenceProps) => {
  return (
    <Layout>
      <NextSeo
        title={occurrence.title}
        canonical={occurrence.absoluteUrl}
        description={occurrence.summary}
      />
      <ModuleContainer>
        <ModuleDetail module={occurrence} />
      </ModuleContainer>
    </Layout>
  );
};
export default OccurrenceDetailPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let occurrence = {};
  let notFound = false;
  const { slug } = params || {};

  await axios
    .get(`http://${process.env.DJANGO_HOSTNAME}:${process.env.DJANGO_PORT}/api/occurrences/${slug}/`)
    .then((response) => {
      occurrence = response.data;
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
      occurrence,
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
