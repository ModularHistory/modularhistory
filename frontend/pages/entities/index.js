import Head from 'next/head';
import axios from 'axios';

import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import CardMedia from '@material-ui/core/CardMedia';
import CardContent from '@material-ui/core/CardContent';

import Layout from "../../components/layout";


export default function Entities({ entities }) {
  return (
    <Layout title={"Entities"}>
      {entities.map(entity => (
        <Card key={entity['pk']}>
          <CardHeader>{entity.name}</CardHeader>
          {entity['serialized_images'].length > 0 &&
            <CardMedia
              component={'img'}
              src={entity['serialized_images'][0]['src_url']}
              // temporary alt
              alt={`Failed to load: ${entity['serialized_images'][0]['src_url']}`}
            />
          }
          <CardContent
            dangerouslySetInnerHTML={{__html: entity.description}}
          />
        </Card>
      ))}
      <pre>{JSON.stringify(entities, null, 4)}</pre>
    </Layout>
  );
}


export async function getServerSideProps() {
  console.log("requesting entities from DRF");
  const entitiesReq = await axios.get("http://drf:8001/entities/api/");
  console.log("received entities from DRF");
  // TODO: catch errors
  const entities = entitiesReq.data.results

  return {
    props: {
      entities: entities,
    },
  };
}
