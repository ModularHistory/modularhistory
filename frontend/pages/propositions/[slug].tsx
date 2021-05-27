import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { PropositionModule } from "@/interfaces";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

interface PropositionProps {
  proposition: PropositionModule;
}

/**
 * A page that renders the HTML of a single proposition.
 */
const Proposition: FC<PropositionProps> = ({ proposition }: PropositionProps) => {
  return (
    <Layout title={proposition.summary}>
      <ModuleContainer>
        <ModuleDetail module={proposition} />
      </ModuleContainer>
    </Layout>
  );
};
export default Proposition;

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
        premises
      }
    }`,
  };
  await axiosWithoutAuth
    .post("http://django:8000/graphql/", body)
    .then((response) => {
      proposition = response.data.data.proposition;
    })
    .catch((_error) => {
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
