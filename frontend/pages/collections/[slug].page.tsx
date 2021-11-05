import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { Collection } from "@/types/modules";
import { Box, Card, CardContent, Container } from "@mui/material";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { NextSeo } from "next-seo";
import Link from "next/link";
import { FC } from "react";
import {
  EmailIcon,
  EmailShareButton,
  FacebookIcon,
  FacebookShareButton,
  TwitterIcon,
  TwitterShareButton,
} from "react-share";

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
        <Box sx={{ m: 3, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Card sx={{ maxWidth: 300, alignItems: "center", justifyContent: "center" }}>
            <CardContent>
              <Typography sx={{ fontSize: 14 }} color="text.secondary" gutterBottom align="center">
                Share the Collection
              </Typography>
              <Grid container spacing={2} alignItems="center" justifyContent="center">
                <Grid item>
                  <FacebookShareButton
                    url={`https://modularhistory.com/collections/${collection.slug}`}
                    quote={collection.title}
                  >
                    <FacebookIcon size={36} />
                  </FacebookShareButton>
                </Grid>
                <Grid item>
                  <TwitterShareButton
                    url={`https://modularhistory.com/collections/${collection.slug}`}
                    title={collection.title}
                  >
                    <TwitterIcon size={36} />
                  </TwitterShareButton>
                </Grid>
                <Grid item>
                  <EmailShareButton
                    url={`https://modularhistory.com/collections/${collection.slug}`}
                    subject={collection.title}
                  >
                    <EmailIcon size={36} />
                  </EmailShareButton>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Box>
      </Container>
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
