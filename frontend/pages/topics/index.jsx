import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import axios from "axios";
import Layout from "../../components/Layout";


export default function Topics({ topicsData }) {
  const topics = topicsData["results"] || [];

  //Style for the anchor used in topicNames
  const topicAnchorStyle = {
    color: 'black',
  }
  const topicNames = topics.map((topic) => (
    <Grid item key={topic['key']} xs={6} sm={6} md={6}>
      <a style={topicAnchorStyle} href={'./search?content_types=occurrences.occurrence&content_types=quotes.quote&content_types=images.image&content_types=sources.source&query=' + topic['key']}><u><strong>{topic['key']}</strong></u></a>
    </Grid>
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
