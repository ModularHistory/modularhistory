import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { EntityModule } from "@/interfaces";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

interface EntityProps {
  entity: EntityModule;
}

/**
 * A page that renders the HTML of a single entity.
 */
const Entity: FC<EntityProps> = ({ entity }: EntityProps) => {
  return (
    <Layout title={entity.name}>
      <ModuleContainer>
        <ModuleDetail module={entity} />
      </ModuleContainer>
    </Layout>
  );
};
export default Entity;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let entity = {};
  const { slug } = params;
  const body = {
    query: `{
      entity(slug: "${slug}") {
        name
        slug
        description
        cachedImages
        model
        adminUrl
      }
    }`,
  };
  await axiosWithoutAuth
    .post("http://django:8000/graphql/", body)
    .then((response) => {
      entity = response.data.data.entity;
    })
    .catch((_error) => {
      entity = null;
    });

  if (!entity) {
    // https://nextjs.org/blog/next-10#notfound-support
    return {
      notFound: true,
    };
  }

  return {
    props: {
      entity,
    },
    revalidate: 10,
  };
};

export const getStaticPaths: GetStaticPaths = async () => {
  return {
    paths: [],
    fallback: "blocking",
  };
};
