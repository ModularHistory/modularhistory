import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import axios from "axios";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { FC } from "react";
import Layout from "../../components/Layout";

interface TopicsProps {
  topicsData: any;
}

const Topics: FC<TopicsProps> = ({ topicsData }: TopicsProps) => {
  const topics = topicsData["data"]["topics"] || [];

  //Style for the anchor used in topicNames
  const topicAnchorStyle = {
    color: "black",
  };

  const topicNames = topics.map((topic) => (
    <Grid item key={topic["name"]} xs={4}>
      <Link href={`/topics/${topic["slug"]}`}>
        <a style={topicAnchorStyle}>
          <strong>{topic["name"]}</strong>
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout title={"Topics"}>
      <Container>
        <h1 className="text-center">Topics</h1>
        <Grid container spacing={2}>
          {topicNames}
        </Grid>
      </Container>
    </Layout>
  );
};

export default Topics;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let topicsData = {};

  await axios
    .get("http://django:8000/graphql/?query={topics{name%20slug}}", {})
    .then((response) => {
      topicsData = response.data;
    })
    .catch((error) => {
      // console.error(error);
    });

  return {
    props: {
      topicsData,
    },
  };
};
