import Layout from "@/components/Layout";
import ModuleContainer from "@/components/moduledetails/ModuleContainer";
import axios from "axios";

export default function Quote({quote}) {
  return (
    <Layout>
      <ModuleContainer module={quote}/>
    </Layout>
  )
}

export async function getStaticProps({params}) {
  let quote = {};
  const {pk} = params;

  await axios
    .get(`http://django:8000/api/quotes/${pk}/`,)
    .then((response) => {
      quote = response.data;
    })
    .catch((error) => {
      // TODO: how should we handle errors here?
    });

  return {
    props: {
      quote
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
