import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import { Quote } from "@/types/modules";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import Link from "next/link";
import { FC } from "react";

interface QuotesProps {
  quotesData: {
    results: Quote[];
    totalPages: number;
  };
}

const Quotes: FC<QuotesProps> = ({ quotesData }: QuotesProps) => {
  const quotes = quotesData["results"] || [];
  const quoteCards = quotes.map((quote) => (
    <Grid item key={quote.slug} xs={6} sm={4} md={3}>
      <Link href={`/quotes/${quote.slug}`} prefetch={false}>
        <a>
          <ModuleUnionCard module={quote} />
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout>
      <NextSeo
        title={"Quotes"}
        canonical={"/quotes"}
        description={
          "Search historical quotes from persons of interest, or search quotes related to a topic of interest."
        }
      />
      <Container>
        <PageHeader>Quotes</PageHeader>
        <Pagination count={quotesData["totalPages"]} />
        <Grid container spacing={2}>
          {quoteCards}
        </Grid>
        <Pagination count={quotesData["totalPages"]} />
      </Container>
    </Layout>
  );
};

export default Quotes;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let quotesData = {};

  await axiosWithoutAuth
    .get("http://django:8002/api/quotes/", { params: context.query })
    .then((response) => {
      quotesData = response.data;
    });

  return {
    props: {
      quotesData,
    },
  };
};
