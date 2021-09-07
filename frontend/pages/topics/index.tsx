import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { Topic } from "@/types/modules";
import Button from "@material-ui/core/Button";
import Container from "@material-ui/core/Container";
import axios from "axios";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { FC } from "react";

interface TopicsProps {
  topicsData: {
    topics: Pick<Topic, "name" | "slug">[];
  };
}

const Topics: FC<TopicsProps> = ({ topicsData }: TopicsProps) => {
  const topics = topicsData.topics || [];

  return (
    <Layout title={"Topics"}>
      <Container>
        <PageHeader>Topics</PageHeader>
        <div style={{ marginBottom: "2rem", textAlign: "center" }}>
          {topics.map((topic) => (
            <Link href={`/topics/${topic.slug}`} key={topic.name} passHref>
              <Button
                component="a"
                sx={{
                  color: "black",
                  margin: "0.6rem 1.2rem",
                  display: "inline-block",
                }}
              >
                {topic.name}
              </Button>
            </Link>
          ))}
        </div>
      </Container>
    </Layout>
  );
};

export default Topics;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async () => {
  let topicsData = {};

  await axios
    .get("http://django:8000/graphql/", {
      params: { query: "{ topics { name slug } }" },
    })
    .then(({ data }) => {
      topicsData = data.data;
    });

  return {
    props: {
      topicsData,
    },
  };
};
