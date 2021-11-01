import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import { Collection } from "@/types/modules";
import { CardContent } from "@mui/material";
import Grid from "@mui/material/Grid";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import Link from "next/link";
import { FC } from "react";
import { Card, Container } from "react-bootstrap";

interface CollectionProps {
  collectionsData: {
    results: Collection[];
    totalPages: number;
  };
}

const Collections: FC<CollectionProps> = ({ collectionsData }: CollectionProps) => {
  //Grid Component for collection card
  const collections = collectionsData["results"] || [];
  const collectionCards = collections.map((collection) => (
    <Grid item key={collection.slug} xs={6} sm={4} md={3}>
      <Link href={`/collections/${collection.slug}`}>
        <a>
          <Card>
            <CardContent>{collection.title}</CardContent>
          </Card>
        </a>
      </Link>
    </Grid>
  ));
  return (
    <Layout>
      <NextSeo
        title={"Collections"}
        canonical={"/collections"}
        description={
          "Browse collections of historical occurrences, entities, sources, and more related to your topics of interest."
        }
      />
      <PageHeader>Collections</PageHeader>
      <Pagination count={collectionsData["totalPages"]} />
      <Container>
        <Grid container spacing={2}>
          {collectionCards}
        </Grid>
      </Container>
    </Layout>
  );
};

export default Collections;

export const getServerSideProps: GetServerSideProps = async (context) => {
  let collectionsData = {};

  await axiosWithoutAuth
    .get("http://django:8000/api/collections/", { params: context.query })
    .then((response) => {
      collectionsData = response.data;
    });

  return {
    props: {
      collectionsData,
    },
  };
};
