import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { ModuleUnion, Topic } from "@/types/modules";
import { Divider } from "@mui/material";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import axios from "axios";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import Link from "next/link";
import { FC } from "react";

interface TopicsProps {
  topicsData: {
    topics: Pick<Topic, "name" | "slug" | "model" | "propositions">[];
  };
  module: ModuleUnion;
  className?: string;
}

const Topics: FC<TopicsProps> = ({ topicsData }: TopicsProps) => {
  const topics = topicsData.topics || [];
  const topicsByLetters: Record<string, typeof topics> = {};
  topics.map((topic) => {
    const firstLetter = topic.name[0].toUpperCase();
    topicsByLetters[firstLetter] = topicsByLetters[firstLetter] || []; //create array if not created already
    topicsByLetters[firstLetter].push(topic);
  });

  return (
    <Layout>
      <NextSeo
        title={"Topics"}
        canonical={"/topics"}
        description={"Browse and learn about the history of your topics of interest."}
      />
      <Container>
        <PageHeader>Topics</PageHeader>
        <div style={{ marginBottom: "2rem", textAlign: "center" }}>
          {Object.keys(topicsByLetters).map((key) => (
            <>
              <Divider sx={{ my: 2 }}>{key}</Divider>
              {topicsByLetters[key].map((topic) => (
                <Link href={`/topics/${topic.slug}`} key={topic.name} passHref prefetch={false}>
                  <Button
                    component="a"
                    variant="outlined"
                    size="small"
                    sx={{
                      color: "black",
                      margin: "0.6rem 1.2rem",
                      display: "inline-block",
                      fontSize: "1rem",
                      border: ".08rem solid black",
                    }}
                  >
                    {`${topic.name} (${topic.propositions.length})`}
                  </Button>
                </Link>
              ))}
            </>
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
    .get(`http://${process.env.DJANGO_HOST}:${process.env.DJANGO_PORT}/graphql/`, {
      params: { query: "{ topics { name slug propositions { slug } } }" },
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
