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
  const topics = topicsData["data"]["allTopics"] || [];

  //Style for the anchor used in topicNames
  const topicAnchorStyle = {
    color: "black",
  };

  const topicNames = topics.map((topic) => (
    <Grid item key={topic["key"]} xs={4}>
      <Link href={`/search?topics=${topic["pk"]}`}>
        <a style={topicAnchorStyle}>
          <strong>{topic["key"]}</strong>
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout title={"Topics"}>
      <Container>
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
    .get("http://django:8000/graphql/?query={allTopics{name%20pk}}", {})
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
