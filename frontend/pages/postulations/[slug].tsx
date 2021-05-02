import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { PostulationModule } from "@/interfaces";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

interface PostulationProps {
  postulation: PostulationModule;
}

/**
 * A page that renders the HTML of a single postulation.
 */
const Postulation: FC<PostulationProps> = ({ postulation }: PostulationProps) => {
  return (
    <Layout title={postulation["summary"]}>
      <ModuleContainer>
        <ModuleDetail module={postulation} />
      </ModuleContainer>
    </Layout>
  );
};
export default Postulation;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let postulation = {};
  const { slug } = params;
  const body = {
    query: `{
      postulation(slug: "${slug}") {
        summary
        elaboration
        model
        adminUrl
      }
    }`,
  };
  await axiosWithoutAuth
    .post("http://django:8000/graphql/", body)
    .then((response) => {
      postulation = response.data.data.postulation;
    })
    .catch((error) => {
      // console.error(error);
    });

  return {
    props: {
      postulation,
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
