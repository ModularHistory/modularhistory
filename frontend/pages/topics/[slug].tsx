import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { Topic } from "@/interfaces";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

interface TopicProps {
  topic: Topic;
}

/**
 * A page that renders the HTML of a single topic.
 */
const TopicDetailPage: FC<TopicProps> = ({ topic }: TopicProps) => {
  return (
    <Layout title={topic.name}>
      <ModuleContainer>
        <ModuleDetail module={topic} />
      </ModuleContainer>
    </Layout>
  );
};
export default TopicDetailPage;

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
    .catch((_error) => {
      topic = null;
    });
  if (!topic) {
    // https://nextjs.org/blog/next-10#notfound-support
    return {
      notFound: true,
    };
  }
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
