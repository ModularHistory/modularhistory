import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { ModuleUnion, Topic } from "@/types/modules";
import { Card } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { styled } from "@material-ui/core/styles";
import axios from "axios";
import { GetServerSideProps } from "next";
import Link from "next/link";
import React, { FC } from "react";

const StyledTopicCard = styled(Card)({
  quotes: '"“" "”" "‘" "’"',
  cursor: "pointer",
  position: "relative",
  textOverflow: "ellipsis",
  minHeight: "5rem",
  width: "20rem",
  color: "black",
  display: "inline-block",
  justifyContent: "center",
  "&:first-child": {
    marginTop: "0 !important",
  },
  "& .fa": {
    "-webkit-text-stroke": "initial",
    textShadow: "none",
  },
  "&.image-card": {
    "& .card-body": {
      "& p": {
        marginBottom: "1rem",
      },
    },
    "& .image-credit": {
      display: "none",
    },
  },
  "& .img-bg": {
    position: "absolute",
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    opacity: "0.8",
    backgroundColor: "black",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
    backgroundSize: "100% auto",
    "&:hover": {
      opacity: "0.9",
    },
  },
});

export { StyledTopicCard };

interface TopicsProps {
  topicsData: {
    topics: Pick<Topic, "name" | "slug" | "model">[];
  };
  module: ModuleUnion;
  className?: string;
}

const Topics: FC<TopicsProps> = ({ topicsData, className }: TopicsProps) => {
  const topics = topicsData.topics || [];

  return (
    <Layout title={"Topics"}>
      <Container>
        <PageHeader>Topics</PageHeader>
        <div style={{ marginBottom: "2rem", textAlign: "center" }}>
          {topics.map((topic) => (
            <Link href={`/topics/${topic.slug}`} key={topic.name} passHref>
              <StyledTopicCard className={`m-2 ${className || ""}`} data-type={topic.model}>
                <h3>{topic.name}</h3>
              </StyledTopicCard>
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
