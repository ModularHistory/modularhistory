import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { Source } from "@/interfaces";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

interface SourceProps {
  source: Source;
}

/**
 * A page that renders the HTML of a single source.
 */
const SourceDetailPage: FC<SourceProps> = ({ source }: SourceProps) => {
  return (
    <Layout title={source.title || source.citationString}>
      <ModuleContainer>
        <ModuleDetail module={source} />
      </ModuleContainer>
    </Layout>
  );
};
export default SourceDetailPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let source = {};
  const { slug } = params;
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
    .catch(() => {
      source = null;
    });

  if (!source) {
    // https://nextjs.org/blog/next-10#notfound-support
    return {
      notFound: true,
    };
  }

  return {
    props: {
      source,
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
