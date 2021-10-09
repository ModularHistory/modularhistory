import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { Entity } from "@/types/modules";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

interface EntityProps {
  entity: Entity;
}

/**
 * A page that renders the HTML of a single entity.
 */
const EntityDetailPage: FC<EntityProps> = ({ entity }: EntityProps) => {
  return (
    <Layout title={entity.name}>
      <ModuleContainer>
        <ModuleDetail module={entity} />
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
