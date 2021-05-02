import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { TopicModule } from "@/interfaces";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

interface TopicProps {
  topic: TopicModule;
}

/**
 * A page that renders the HTML of a single topic.
 */
const Topic: FC<TopicProps> = ({ topic }: TopicProps) => {
  return (
    <Layout title={topic["name"]}>
      <ModuleContainer>
        <ModuleDetail module={topic} />
      </ModuleContainer>
    </Layout>
  );
};
export default Topic;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let topic = {};
  const { slug } = params;
  const body = {
    query: `{
      topic(slug: "${slug}") {
        name
        slug
        description
        model
        adminUrl
      }
    }`,
  };
  await axiosWithoutAuth
    .post("http://django:8000/graphql/", body)
    .then((response) => {
      topic = response.data.data.topic;
    })
    .catch((error) => {
      // console.error(error);
    });

  // via Rest API
  // await axiosWithoutAuth
  //   .get(`http://django:8000/api/topics/${slug}`)
  //   .then((response) => {
  //     topic = response.data;
  //     console.log(topic);
  //   })
  //   .catch((error) => {
  //     // console.error(error);
  //   });

  return {
    props: {
      topic,
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
