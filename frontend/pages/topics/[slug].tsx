import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { Topic } from "@/types/modules";
import { GetStaticPaths, GetStaticProps } from "next";
import Link from "next/link";
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
        <PageHeader>{topic.name}</PageHeader>
        {topic.description && <p dangerouslySetInnerHTML={{ __html: topic.description }} />}
        {topic.propositions &&
          topic.propositions.map((proposition) => (
            <Link href={`/propositions/${proposition.slug}`} key={proposition.slug}>
              <a>
                <div>
                  <p dangerouslySetInnerHTML={{ __html: proposition.summary }} />
                </div>
              </a>
            </Link>
          ))}
      </ModuleContainer>
    </Layout>
  );
};
export default TopicDetailPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let topic = {};
  let notFound = false;
  const { slug } = params || {};
  const body = {
    query: `{
      topic(slug: "${slug}") {
        name
        slug
        description
        model
        adminUrl
        propositions {
          slug
          summary
          elaboration
          cachedImages
        }
      }
    }`,
  };
  await axiosWithoutAuth
    .post("http://django:8000/graphql/", body)
    .then((response) => {
      topic = response.data.data.topic;
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
      topic,
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
