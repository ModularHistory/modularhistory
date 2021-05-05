import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { OccurrenceModule } from "@/interfaces";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { FC } from "react";

interface OccurrenceProps {
  occurrence: OccurrenceModule;
}

/**
 * A page that renders the HTML of a single occurrence.
 */
const Occurrence: FC<OccurrenceProps> = ({ occurrence }: OccurrenceProps) => {
  return (
    <Layout title={occurrence.title}>
      <ModuleContainer>
        <ModuleDetail module={occurrence} />
      </ModuleContainer>
    </Layout>
  );
};
export default Occurrence;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let occurrence = {};
  const { slug } = params;

  await axios
    .get(`http://django:8000/api/occurrences/${slug}/`)
    .then((response) => {
      occurrence = response.data;
    })
    .catch((error) => {
      // TODO: how should we handle errors here?
    });

  return {
    props: {
      occurrence,
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
