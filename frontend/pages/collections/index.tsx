import ModuleCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import { Quote } from "@/types/modules";
import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { FC, useState } from "react";
import HTMLEllipsis from "react-lines-ellipsis/lib/html";



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

  const [cards, setCards] = useState([]); // instantiate cards as a empty Array

  const addCard = () => {
    // create a new array with the old values and the new random one
    const newCards = [...cards, Math.floor(Math.random() * 100)];

    setCards(newCards);
  };

  const removeCard = (cardIndex) => {
    // create a new array without the item that you are removing
    const newCards = cards.filter((card, index) => index !== cardIndex);

    setCards(newCards);
  };


  return (
    <Layout title={"Collections"}>
      {/* <h5>This is the new page</h5> */}
      <div style={{ display: "flex" }}>
        <Button
          style={{ marginLeft: "auto" }}
          onClick={() => addCard()}
        >
          Click
        </Button>
      </div>
    </Layout>
  );
};

export default Quotes;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let quotesData = {};

  // await axiosWithoutAuth
  //   .get("http://django:8000/api/quotes/", { params: context.query })
  //   .then((response) => {
  //     quotesData = response.data;
  //   });

  return {
    props: {
      quotesData,
    },
  };
};
