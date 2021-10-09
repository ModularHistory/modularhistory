import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { Entity } from "@/types/modules";
import { Card, CardContent, CardHeader } from "@mui/material";
import { GetStaticPaths, GetStaticProps } from "next";
import Link from "next/link";
import React, { FC } from "react";
import HTMLEllipsis from "react-lines-ellipsis/lib/html";

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
        {hasRelatedQuotes && <CardHeader title={`Quotes from ${entity.name}`}></CardHeader>}
        {hasRelatedQuotes &&
          entity.relatedQuotes?.map((relatedQuote) => (
            <Link href={`/quotes/${relatedQuote.slug}`} key={relatedQuote.slug} passHref>
              <a>
                <Card>
                  <CardContent>
                    <HTMLEllipsis unsafeHTML={relatedQuote.bite} maxLine="3" basedOn="words" />
                  </CardContent>
                </Card>
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
