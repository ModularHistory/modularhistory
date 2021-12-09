import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { Source } from "@/types/models";
import { GetStaticPaths, GetStaticProps } from "next";
import { NextSeo } from "next-seo";
import { FC } from "react";

interface SourceProps {
  source: Source;
}

/**
 * A page that renders the HTML of a single source.
 */
const SourceDetailPage: FC<SourceProps> = ({ source }: SourceProps) => {
  return (
    <Layout>
      <NextSeo
        title={source.title || source.citationString}
        canonical={source.absoluteUrl}
        description={`View details regarding, and quotations from, ${source.citationString}`}
      />
      <ModuleContainer>
        <ModuleDetail module={source} />
      </ModuleContainer>
    </Layout>
  );
};
export default SourceDetailPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let source = {};
  let notFound = false;
  const { slug } = params || {};
  const body = {
    query: `{
      source(slug: "${slug}") {
        title
        citationHtml
        citationString
        attributeeHtml
        model
        adminUrl
      }
    }`,
  };
  await axiosWithoutAuth
    .post("http://django:8000/graphql/", body)
    .then((response) => {
      source = response.data.data.source;
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
      source,
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
