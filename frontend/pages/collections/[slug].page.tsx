import ModuleUnionCard from "@/components/cards/ModuleUnionCard";
import Layout from "@/components/Layout";
import { Collection } from "@/types/modules";
import ShareIcon from "@mui/icons-material/Share";
import { Box, Button, Container, useMediaQuery } from "@mui/material";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { NextSeo } from "next-seo";
import Link from "next/link";
import React, { FC, useState } from "react";
import {
  EmailIcon,
  EmailShareButton,
  FacebookIcon,
  FacebookShareButton,
  TwitterIcon,
  TwitterShareButton,
} from "react-share";
import { GlobalTheme } from "../_app.page";

interface CollectionProps {
  collection: Collection;
}

/**
 * The collections page:
 * http://www.modularhistory.com/collections
 */
const CollectionDetailPage: FC<CollectionProps> = ({ collection }: CollectionProps) => {
  const smallScreen = useMediaQuery<GlobalTheme>((theme) => theme.breakpoints.down("sm"));
  return (
    <Layout>
      <NextSeo
        title={collection.title}
        canonical={"/collections"}
        description={`"${collection.title}", a collection of historical occurrences, entities, sources, and more.`}
      />
      <Box sx={{ m: 2 }}>
        <Typography
          sx={{ fontFamily: "Segoe UI", fontWeight: 500, fontSize: 40 }}
          variant="h4"
          align="center"
        >
          {collection.title}
        </Typography>
      </Box>
      {smallScreen ? (
        <MobileViewComponent collection={collection} />
      ) : (
        <DesktopViewComponent collection={collection} />
      )}
      ;
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

const MobileViewComponent: FC<CollectionProps> = ({ collection }: CollectionProps) => {
  const [showIcons, setShowIcons] = useState(false);
  const onClick = () => {
    setShowIcons(true);
    if (showIcons) {
      setShowIcons(false);
    }
  };
  return (
    <>
      <Container>
        <Grid sx={{ m: 3, display: "flex", alignItems: "center", justifyContent: "flex-end" }}>
          <Grid sx={{ maxWidth: 250, alignItems: "center", justifyContent: "center" }}>
            <Grid
              sx={{
                flexDirection: "column",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Button
                variant="contained"
                color="primary"
                onClick={onClick}
                sx={{ borderRadius: "50%" }}
              >
                <ShareIcon />
              </Button>
              <>
                {showIcons ? (
                  <Grid
                    container
                    spacing={2}
                    alignItems="center"
                    justifyContent="center"
                    sx={{ my: 1 }}
                  >
                    <Grid item>
                      <FacebookShareButton
                        url={`https://modularhistory.com/collections/${collection.slug}`}
                        quote={collection.title}
                      >
                        <FacebookIcon size={36} round={true} />
                      </FacebookShareButton>
                    </Grid>
                    <Grid item>
                      <TwitterShareButton
                        url={`https://modularhistory.com/collections/${collection.slug}`}
                        title={collection.title}
                      >
                        <TwitterIcon size={36} round={true} />
                      </TwitterShareButton>
                    </Grid>
                    <Grid item>
                      <EmailShareButton
                        url={`https://modularhistory.com/collections/${collection.slug}`}
                        subject={collection.title}
                      >
                        <EmailIcon size={36} round={true} />
                      </EmailShareButton>
                    </Grid>
                  </Grid>
                ) : null}
              </>
            </Grid>
          </Grid>
        </Grid>
      </Container>
    </>
  );
};

const DesktopViewComponent: FC<CollectionProps> = ({ collection }: CollectionProps) => {
  return (
    <Container>
      <Grid sx={{ m: 3, display: "flex", alignItems: "center", justifyContent: "flex-end" }}>
        <Grid sx={{ maxWidth: 250, alignItems: "center", justifyContent: "center" }}>
          <Grid container spacing={2} alignItems="center" justifyContent="center">
            <Grid item>
              <FacebookShareButton
                url={`https://modularhistory.com/collections/${collection.slug}`}
                quote={collection.title}
              >
                <FacebookIcon size={36} round={true} />
              </FacebookShareButton>
            </Grid>
            <Grid item>
              <TwitterShareButton
                url={`https://modularhistory.com/collections/${collection.slug}`}
                title={collection.title}
              >
                <TwitterIcon size={36} round={true} />
              </TwitterShareButton>
            </Grid>
            <Grid item>
              <EmailShareButton
                url={`https://modularhistory.com/collections/${collection.slug}`}
                subject={collection.title}
              >
                <EmailIcon size={36} round={true} />
              </EmailShareButton>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Container>
  );
};
