import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import { Collection } from "@/types/modules";
import Grid from "@mui/material/Grid";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

interface CollectionProps {
  collection: Collection;
}

/**
 * A page that renders the HTML of a single entity.
 */
const CollectionDetailPage: FC<CollectionProps> = ({ collection }: CollectionProps) => {
  return (
    <Layout title={collection.title}>
      <Grid container spacing={2}>
        {collection.propositions.map((proposition) => (
          <Grid item key={proposition.slug}>
            {" "}
            <ModuleUnionCard module={proposition} />
          </Grid>
        ))}
        {collection.quotes.map((quote) => (
          <Grid item key={quote.slug}>
            {" "}
            <ModuleUnionCard module={quote} />
          </Grid>
        ))}
        {collection.sources.map((source) => (
          <Grid item key={source.slug}>
            {" "}
            <ModuleUnionCard module={source} />
          </Grid>
        ))}
        {collection.propositions.map((proposition) => (
          <Grid item key={proposition.slug}>
            {" "}
            <ModuleUnionCard module={proposition} />
          </Grid>
        ))}
        {collection.propositions.map((proposition) => (
          <Grid item key={proposition.slug}>
            {" "}
            <ModuleUnionCard module={proposition} />
          </Grid>
        ))}
      </Grid>
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
