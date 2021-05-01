import axiosWithoutAuth from "@/axiosWithoutAuth";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import CardHeader from "@material-ui/core/CardHeader";
import CardMedia from "@material-ui/core/CardMedia";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { FC } from "react";
import Layout from "../../components/Layout";
import Pagination from "../../components/Pagination";

interface QuotesProps {
  quotesData: any;
}

const Quotes: FC<QuotesProps> = ({ quotesData }: QuotesProps) => {
  const quotes = quotesData["results"] || [];
  const quoteCards = quotes.map((quote) => (
    <Grid item key={quote["slug"]} xs={6} sm={4} md={3}>
      <Link href={`/quotes/${quote["slug"]}`}>
        <a>
          <Card>
            <CardHeader title={quote["title"]} />
            {quote["serialized_images"].length > 0 && (
              <CardMedia
                style={{ height: 0, paddingTop: "100%" }}
                image={quote["serialized_images"][0]["src_url"]}
              />
            )}
            <CardContent dangerouslySetInnerHTML={{ __html: quote["truncated_description"] }} />
          </Card>
        </a>
      </Link>
    </Grid>
  ));

  return (
    <Layout title={"Quotes"}>
      <Container>
        <Pagination count={quotesData["total_pages"]} />
        <Grid container spacing={2}>
          {quoteCards}
        </Grid>
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
