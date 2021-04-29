import Layout from "@/components/Layout";
import ModuleContainer from "@/components/moduledetails/ModuleContainer";
import { EntityModule } from "@/interfaces";
import axios from "axios";
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
    <Layout title={entity["name"]}>
      <ModuleContainer module={entity} />
    </Layout>
  );
};
export default Entity;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let entity = {};
  const { slug } = params;

  await axios
    .get(`http://django:8000/api/entities/${slug}/`)
    .then((response) => {
      entity = response.data;
    })
    .catch((error) => {
      // TODO: how should we handle errors here?
    });

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
