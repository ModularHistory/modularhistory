import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { FC } from "react";
import HTMLEllipsis from "react-lines-ellipsis/lib/html";

interface QuotesProps {
  quotesData: any;
}

const Quotes: FC<QuotesProps> = ({ quotesData }: QuotesProps) => {
  const quotes = quotesData["results"] || [];
  const quoteCards = quotes.map((quote) => (
    <Grid item key={quote.slug} xs={6} sm={4} md={3}>
      <Link href={`/quotes/${quote.slug}`}>
        <a>
          <ModuleCard module={quote}>
            <blockquote className="blockquote">
              <HTMLEllipsis unsafeHTML={quote.bite} maxLine="5" basedOn="words" />
              {quote.attributeeString && (
                <footer
                  className="blockquote-footer"
                  dangerouslySetInnerHTML={{ __html: quote.attributeeString }}
                />
              )}
            </blockquote>
          </ModuleCard>
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout title={"Quotes"}>
      <Container>
        <PageHeader>Quotes</PageHeader>
        <Pagination count={quotesData["total_pages"]} />
        <Grid container spacing={2}>
          {quoteCards}
        </Grid>
        <Pagination count={quotesData["total_pages"]} />
      </Container>
    </Layout>
  );
};

export default Quotes;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let quotesData = {};

  await axiosWithoutAuth
    .get("http://django:8000/api/quotes/", { params: context.query })
    .then((response) => {
      quotesData = response.data;
    })
    .catch((error) => {
      // console.error(error);
    });

  return {
    props: {
      quotesData,
    },
  };
};
