import Layout from "@/components/Layout";
import {Container, useMediaQuery} from "@material-ui/core";
import axios from "axios";

export default function StaticPage({page}) {
  // check if the viewport width is less than 600px
  const isSmall = useMediaQuery("@media (max-width:600px)");

  return (
    <Layout>
      <Container style={{padding: `20px ${isSmall ? "20px" : "80px"}`, maxWidth: "50rem"}}>
        <h1>{page["title"]}</h1>
        <div dangerouslySetInnerHTML={{__html: page["content"]}}/>
      </Container>
    </Layout>
  );
}

export async function getStaticProps({params}) {
  let page = {};
  const {path} = params;

  await axios
    .get(`http://django:8000/api/staticpages//${path}/`,)
    .then((response) => {
      page = response.data;
    })
    .catch((error) => {
      // TODO: how should we handle errors here?
    });

  return {
    props: {
      page
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