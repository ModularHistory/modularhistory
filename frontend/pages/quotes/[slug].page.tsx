import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { Quote } from "@/types/modules";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { NextSeo } from "next-seo";
import { FC } from "react";

interface QuoteProps {
  quote: Quote;
}

/**
 * A page that renders the HTML of a single quote.
 */
const QuoteDetailPage: FC<QuoteProps> = ({ quote }: QuoteProps) => {
  return (
    <Layout>
      <NextSeo
        title={quote.title}
        canonical={quote.absoluteUrl}
        description={`Quote by ${quote.attributeeString}, ${quote.dateString}: ${quote.bite} ...`}
      />
      <ModuleContainer>
        <ModuleDetail module={quote} />
      </ModuleContainer>
    </Layout>
  );
};
export default QuoteDetailPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let quote = {};
  let notFound = false;
  const { slug } = params || {};

  await axios
    .get(`http://django:8002/api/quotes/${slug}/`)
    .then((response) => {
      quote = response.data;
    })
    .catch((error) => {
      if (error.response?.status === 404) {
        notFound = true;
      } else {
        throw error;
      }
    });

  return {
    props: { quote },
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
