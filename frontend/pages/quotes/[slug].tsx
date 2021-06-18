import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { Quote } from "@/interfaces";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

interface QuoteProps {
  quote: Quote;
}

/**
 * A page that renders the HTML of a single quote.
 */
const QuoteDetailPage: FC<QuoteProps> = ({ quote }: QuoteProps) => {
  return (
    <Layout title={quote.title}>
      <ModuleContainer>
        <ModuleDetail module={quote} />
      </ModuleContainer>
    </Layout>
  );
};
export default QuoteDetailPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let quote = {};
  const { slug } = params;

  await axios
    .get(`http://django:8000/api/quotes/${slug}/`)
    .then((response) => {
      quote = response.data;
    })
    .catch(() => {
      quote = null;
    });

  if (!quote) {
    // https://nextjs.org/blog/next-10#notfound-support
    return {
      notFound: true,
    };
  }

  return {
    props: { quote },
    revalidate: 10,
  };
};

export const getStaticPaths: GetStaticPaths = async () => {
  return {
    paths: [],
    fallback: "blocking",
  };
};
