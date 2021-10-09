import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { Entity } from "@/types/modules";
import { Card, CardContent, CardHeader, styled } from "@mui/material";
import { GetStaticPaths, GetStaticProps } from "next";
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

interface EntityProps {
  entity: Entity;
}

/**
 * A page that renders the HTML of a single entity.
 */
const EntityDetailPage: FC<EntityProps> = ({ entity }: EntityProps) => {
  const hasRelatedQuotes = (entity.relatedQuotes && entity.relatedQuotes.length) || undefined;
  //const hasRelatedEntities = entity.relatedEntities && entity.relatedEntities.length || undefined; #TODO: fix in entity schema

  return (
    <Layout title={entity.name}>
      <ModuleContainer>
        <ModuleDetail module={entity} />
      </ModuleContainer>
      <ModuleContainer>
        {hasRelatedQuotes && (
          <CardHeader
            title={`Quotes from ${entity.name}:`}
            style={{ textAlign: "center" }}
          ></CardHeader>
        )}
        {hasRelatedQuotes &&
          entity.relatedQuotes?.map((relatedQuote) => (
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
