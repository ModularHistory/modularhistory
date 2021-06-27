import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { Proposition } from "@/interfaces";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

interface PropositionProps {
  proposition: Proposition;
}

/**
 * A page that renders the HTML of a single proposition.
 */
const PropositionDetailPage: FC<PropositionProps> = ({ proposition }: PropositionProps) => {
  return (
    <Layout title={proposition.summary}>
      <ModuleDetail module={proposition} />
    </Layout>
  );
};
export default PropositionDetailPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let proposition = {};
  const { slug } = params;
  const body = {
    query: `{
      proposition(slug: "${slug}") {
        summary
        elaboration
        model
        adminUrl
        certainty
        arguments {
          pk
          type
          explanation
          premises {
            absoluteUrl
            dateString
            certainty
            slug
            summary
            elaboration
          }
        }
        conflictingPropositions {
          slug
          absoluteUrl
          summary
        }
      }
    }`,
  };
  await axiosWithoutAuth
    .post("http://django:8000/graphql/", body)
    .then((response) => {
      proposition = response.data.data.proposition;
    })
    .catch(() => {
      proposition = null;
    });

  if (!proposition) {
    // https://nextjs.org/blog/next-10#notfound-support
    return {
      notFound: true,
    };
  }

  return {
    props: {
      proposition,
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
