import Layout from "@/components/Layout";
import ModuleContainer from "@/components/moduledetails/ModuleContainer";
import axios from "axios";

export default function Occurrence({occurrence}) {
  return (
    <Layout>
      <ModuleContainer module={occurrence}/>
    </Layout>
  )
}

export async function getStaticProps({params}) {
  let occurrence = {};
  const {slug} = params;

  await axios
    .get(`http://django:8000/api/occurrences/${slug}/`,)
    .then((response) => {
      occurrence = response.data;
    })
    .catch((error) => {
      // TODO: how should we handle errors here?
    });

  return {
    props: {
      occurrence
    },
    revalidate: 10,
  };
}

export async function getStaticPaths() {
  return {
    paths: [],
    fallback: "blocking"
  };
}
