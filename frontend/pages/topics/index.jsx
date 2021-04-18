import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import axios from "axios";
import Layout from "../../components/Layout";


export default function Topics({ topicsData }) {
  const topics = topicsData["results"] || [];

  //replace <p>{topic['name']}</p> with <a> to SERP topics in version 2
  const topicNames = topics.map((topic) => (
    <p>{topic['name']}</p>
  ));

  return (
    <Layout title={"Topics"}>
      <Container>
        <Grid container spacing={2}>
          {topicNames}
        </Grid>
      </Container>
    </Layout>
  );
}

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export async function getServerSideProps(context) {
  let topicsData = {};

  await axios
    .get("http://django:8000/api/topics/", { params: context.query })
    .then((response) => {
      topicsData = response.data;
    })
    .catch((error) => {
      // console.error(error);
    });

  return {
    props: {
      topicsData,
    },
  };
}
