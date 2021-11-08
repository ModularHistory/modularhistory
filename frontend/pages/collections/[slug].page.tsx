import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { Collection } from "@/types/modules";
import Grid from "@mui/material/Grid";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { NextSeo } from "next-seo";
import Link from "next/link";
import { FC } from "react";
import { Container } from "react-bootstrap";

interface CollectionProps {
  collection: Collection;
}

/**
 * The collections page:
 * http://www.modularhistory.com/collections
 */
const CollectionDetailPage: FC<CollectionProps> = ({ collection }: CollectionProps) => {
  return (
    <Layout>
      <NextSeo
        title={collection.title}
        canonical={"/collections"}
        description={`"${collection.title}", a collection of historical occurrences, entities, sources, and more.`}
      />
      <PageHeader>{collection.title}</PageHeader>
      <Container>
        <Grid container spacing={2}>
          {[collection.propositions, collection.entities, collection.quotes, collection.sources]
            .flat()
            .map((module) => (
              <Grid item key={module.slug} xs={6} sm={4} md={3}>
                <Link href={module.absoluteUrl}>
                  <a>
                    <ModuleUnionCard module={module} />
                  </a>
                </Link>
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
