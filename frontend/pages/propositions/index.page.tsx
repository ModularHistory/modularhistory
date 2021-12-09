import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { Proposition } from "@/types/models";
import Container from "@mui/material/Container";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import Link from "next/link";
import { FC } from "react";

interface PropositionsProps {
  topics: {
    name: string;
    slug: string;
    conclusions: Proposition[];
  }[];
}

const Propositions: FC<PropositionsProps> = ({ topics }: PropositionsProps) => {
  return (
    <Layout>
      <NextSeo
        title={"Propositions"}
        canonical={"/propositions"}
        description={"Browse propositions related to topics that interest you."}
      />
      <Container>
        <PageHeader>Propositions</PageHeader>
        {topics &&
          topics.map((topic) => (
            <div key={topic.slug}>
              <h2>{topic.name}</h2>
              <List>
                {topic.conclusions.map((proposition) => (
                  <ListItem key={proposition.slug}>
                    <Link href={`/propositions/${proposition.slug}`} prefetch={false}>
                      <a>
                        <div dangerouslySetInnerHTML={{ __html: proposition.summary }} />
                      </a>
                    </Link>
                  </ListItem>
                ))}
              </List>
            </div>
          ))}
      </Container>
    </Layout>
  );
};

export default Propositions;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async () => {
  let topics;
  const body = {
    query: `{
      topicsWithConclusions {
        name
        slug
        conclusions {
          slug
          summary
        }
      }
    }`,
  };
  await axiosWithoutAuth
    .post("http://django:8000/graphql/", body)
    .then((response) => {
      topics = response.data.data.topicsWithConclusions;
    })
    .catch(() => {
      topics = [];
    });
  return {
    props: {
      topics,
    },
  };
};
