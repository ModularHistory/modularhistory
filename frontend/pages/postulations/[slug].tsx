import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { PostulationModule } from "@/interfaces";
import axios from "axios";
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
    <Layout title={postulation["title"]}>
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

  await axios
    .get(`http://django:8000/api/postulations/${slug}/`)
    .then((response) => {
      postulation = response.data;
    })
    .catch((error) => {
      // TODO: how should we handle errors here?
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
