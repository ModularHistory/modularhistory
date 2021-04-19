import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import CardHeader from "@material-ui/core/CardHeader";
import CardMedia from "@material-ui/core/CardMedia";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import axios from "axios";
import Layout from "../../components/Layout";
import Pagination from "../../components/Pagination";


export default function Entities({ entitiesData }) {
  const entities = entitiesData["results"] || [];

  const entityCards = entities.map((entity) => (
    <Grid item key={entity["pk"]} xs={6} sm={4} md={3}>
      <a href={`entities/${entity["pk"]}`}>
        <Card>
          <CardHeader title={entity["name"]} />
          {entity["serialized_images"].length > 0 && (
            <CardMedia
              style={{ height: 0, paddingTop: "100%" }}
              image={entity["serialized_images"][0]["src_url"]}
            />
          )}
          <CardContent dangerouslySetInnerHTML={{ __html: entity["description"] }} />
        </Card>
      </a>
    </Grid>
  ));

  return (
    <Layout title={"Entities"}>
      <Container>
        <Pagination count={entitiesData["total_pages"]} />
        <Grid container spacing={2}>
          {entityCards}
        </Grid>
      </Container>
      {/*<pre>{JSON.stringify(entitiesData, null, 4)}</pre>*/}
    </Layout>
  );
}

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export async function getServerSideProps(context) {
  let entitiesData = {};

  await axios
    .get("http://django:8000/api/entities/", { params: context.query })
    .then((response) => {
      entitiesData = response.data;
    })
    .catch((error) => {
      // console.error(error);
    });

  return {
    props: {
      entitiesData,
    },
  };
}