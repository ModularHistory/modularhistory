import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import Container from "@material-ui/core/Container";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { FC } from "react";

interface PropositionsProps {
  propositionsData: any;
}

const Propositions: FC<PropositionsProps> = ({ propositionsData }: PropositionsProps) => {
  const propositions = propositionsData["results"] || [];
  const propositionElements = propositions.map((proposition) => (
    <ListItem key={proposition.slug}>
      <Link href={`/propositions/${proposition.slug}`}>
        <a>
          <div dangerouslySetInnerHTML={{ __html: proposition.summary }} />
        </a>
      </Link>
    </ListItem>
  ));

  return (
    <Layout title={"Propositions"}>
      <Container>
        <PageHeader>Propositions</PageHeader>
        <Pagination count={propositionsData["total_pages"]} />
        <List>{propositionElements}</List>
        <Pagination count={propositionsData["total_pages"]} />
      </Container>
    </Layout>
  );
};

export default Propositions;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let propositionsData = {};

  await axiosWithoutAuth
    .get("http://django:8000/api/propositions/", { params: context.query })
    .then((response) => {
      propositionsData = response.data;
    })
    .catch((error) => {
      // console.error(error);
    });

  return {
    props: {
      propositionsData,
    },
  };
};
