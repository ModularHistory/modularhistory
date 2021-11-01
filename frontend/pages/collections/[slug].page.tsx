import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { Collection } from "@/types/modules";
import Grid from "@mui/material/Grid";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { NextSeo } from "next-seo";
import { FC } from "react";
import { Container } from "react-bootstrap";
interface CollectionProps {
  collection: Collection;
}

/**
 * A page that renders the HTML of a single entity.
 */
const CollectionDetailPage: FC<CollectionProps> = ({ collection }: CollectionProps) => {
  return (
    <Layout>
      <NextSeo
        title={"Occurrences"}
        canonical={"/occurrences"}
        description={
          "Browse historical occurrences related to your topics or entities of interest."
        }
      />
      <PageHeader>Collections</PageHeader>
      <Container>
        <Grid container spacing={2}>
          {collection.propositions.map((proposition) => (
            <Grid item key={proposition.slug}>
              <ModuleUnionCard module={proposition} />
            </Grid>
          ))}
          {collection.quotes.map((quote) => (
            <Grid item key={quote.slug}>
              <ModuleUnionCard module={quote} />
            </Grid>
          ))}
          {collection.sources.map((source) => (
            <Grid item key={source.slug}>
              <ModuleUnionCard module={source} />
            </Grid>
          ))}
          {collection.propositions.map((entity) => (
            <Grid item key={entity.slug}>
              <ModuleUnionCard module={entity} />
            </Grid>
          ))}
        </Grid>
      </Container>
    </Layout>
  );
};
export default CollectionDetailPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let collection = {};
  let notFound = false;
  const { slug } = params || {};

  await axios
    .get(`http://django:8000/api/collections/${slug}/`)
    .then((response) => {
      collection = response.data;
    })
    .catch((error) => {
      if (error.response?.status === 404) {
        notFound = true;
      } else {
        throw error;
      }
    });

  return {
    props: { collection },
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
