import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Button from "@material-ui/core/Button";
import Container from "@material-ui/core/Container";
import { createStyles, makeStyles } from "@material-ui/core/styles";
import axios from "axios";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { FC } from "react";

interface TopicsProps {
  topicsData: any;
}

const useStyles = makeStyles(() =>
  createStyles({
    topicLink: {
      color: "black",
      margin: "0.6rem 1.2rem",
      display: "inline-block",
    },
  })
);

const Topics: FC<TopicsProps> = ({ topicsData }: TopicsProps) => {
  const topics = topicsData["data"]["topics"] || [];
  const classes = useStyles();

  return (
    <Layout title={"Topics"}>
      <Container>
        <PageHeader>Topics</PageHeader>
        <div style={{ marginBottom: "2rem", textAlign: "center" }}>
          {topics.map((topic) => (
            <Link href={`/topics/${topic.slug}`} key={topic.name} passHref>
              <Button className={classes.topicLink} component="a">
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
    .get("http://django:8000/graphql/?query={topics{name%20slug}}", {})
    .then((response) => {
      topicsData = response.data;
    });

  return {
    props: {
      topicsData,
    },
  };
};
