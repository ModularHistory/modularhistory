import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { Entity } from "@/types/modules";
import { Card, CardContent, CardHeader, styled, Typography } from "@mui/material";
import { Box } from "@mui/system";
import { GetStaticPaths, GetStaticProps } from "next";
import { NextSeo } from "next-seo";
import Link from "next/link";
import React, { FC } from "react";
import HTMLEllipsis from "react-lines-ellipsis/lib/html";

const EntityRelatedQuoteCard = styled(Card)({
  quotes: '"“" "”" "‘" "’"',
  cursor: "pointer",
  position: "relative",
  textOverflow: "ellipsis",
  minHeight: "5rem",
  marginBottom: "1rem",
  width: "40rem",
  color: "black",
});

const EntityRelatedEntityCard = styled(Card)({
  quotes: '"“" "”" "‘" "’"',
  cursor: "pointer",
  position: "relative",
  textOverflow: "ellipsis",
  minHeight: "1rem",
  marginBottom: "1rem",
  width: "17rem",
  color: "black",
  "&:hover": {
    backgroundColor: "#c4e1ff",
  },
});

interface EntityProps {
  entity: Entity;
}

/**
 * A page that renders the HTML of a single entity.
 */
const EntityDetailPage: FC<EntityProps> = ({ entity }: EntityProps) => {
  return (
    <Layout>
      <NextSeo
        title={entity.name}
        canonical={entity.absoluteUrl}
        description={`Learn about the history of ${entity.name}, including occurrences, quotes, and more related to issues that matter to people today.`}
      />
      <ModuleContainer>
        <ModuleDetail module={entity} />
        {(entity.relatedEntities?.length ?? 0) > 0 && (
          <>
            <CardHeader
              title={`Entitles related to ${entity.name}:`}
              style={{ textAlign: "center" }}
            ></CardHeader>
            <Box sx={{ display: "flex", flexWrap: "wrap", justifyContent: "center" }}>
              {entity.relatedEntities?.map((relatedEntity) => (
                <Link href={`/entities/${relatedEntity.slug}`} key={relatedEntity.slug} passHref>
                  <a>
                    <EntityRelatedEntityCard raised sx={{ margin: "0.3rem" }}>
                      <Typography sx={{ padding: "0.5rem", textAlign: "center" }}>
                        <HTMLEllipsis unsafeHTML={relatedEntity.name} maxLine="1" basedOn="words" />
                      </Typography>
                    </EntityRelatedEntityCard>
                  </a>
                </Link>
              ))}
            </Box>
          </>
        )}
        {(entity.relatedQuotes?.length ?? 0) > 0 && (
          <>
            <CardHeader
              title={`Quotes from ${entity.name}:`}
              style={{ textAlign: "center" }}
            ></CardHeader>
            {entity.relatedQuotes?.map((relatedQuote) => (
              <Link href={`/quotes/${relatedQuote.slug}`} key={relatedQuote.slug} passHref>
                <a>
                  <EntityRelatedQuoteCard raised>
                    {relatedQuote.dateString && (
                      <CardHeader title={relatedQuote.dateString}></CardHeader>
                    )}
                    <CardContent>
                      <HTMLEllipsis unsafeHTML={relatedQuote.bite} maxLine="3" basedOn="words" />
                    </CardContent>
                  </EntityRelatedQuoteCard>
                </a>
              </Link>
            ))}
          </>
        )}
      </ModuleContainer>
    </Layout>
  );
};
export default EntityDetailPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let entity;
  let notFound = false;
  const { slug } = params || {};

  const body = {
    query: `{
        entity(slug: "${slug}") {
          name
          slug
          description
          cachedImages
          model
          adminUrl
          relatedQuotes {
            title
            slug
            bite
            dateString
          }
          relatedEntities {
            name
            description
            slug
          }
        }
      }`,
  };
  await axiosWithoutAuth
    .post("http://django:8000/graphql/", body)
    .then((response) => {
      entity = response.data.data.entity;
    })
    .catch((error) => {
      if (error.response?.status === 404) {
        notFound = true;
      } else {
        throw error;
      }
    });

  return {
    props: {
      entity,
    },
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
