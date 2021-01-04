import Head from 'next/head';
import axios from 'axios';

import Layout from "../../components/layout";
import {
  MDBCard, MDBCardBody, MDBCardImage,
  MDBCardTitle, MDBCardText,
} from "mdbreact";


export default function Entities({ entities }) {
  return (
    <Layout title={"Entities"}>
      {entities.map(entity => (
        <MDBCard key={entity['pk']}>
          {entity['serialized_images'].length > 0 &&
            <MDBCardImage
              src={entity['serialized_images'][0]['src_url']}
              // temporary alt
              alt={`Failed to load: ${entity['serialized_images'][0]['src_url']}`}
            />
          }
          <MDBCardBody>
            <MDBCardTitle>{entity.name}</MDBCardTitle>
            <MDBCardText tag='div'>
              <div dangerouslySetInnerHTML={{__html: entity.description}} />
            </MDBCardText>
          </MDBCardBody>
        </MDBCard>
      ))}
      <pre>{JSON.stringify(entities, null, 4)}</pre>
    </Layout>
  );
}


export async function getServerSideProps() {
  console.log("requesting entities from DRF");
  const entitiesReq = await axios.get("http://dev-backend:8000/entities/api");
  console.log("received entities from DRF");
  // TODO: catch errors
  const entities = entitiesReq.data.results

  if (process.env.ENVIRONMENT === 'dev') {
    for (const entity of entities) {
      for (const image of entity['serialized_images']){
        image['src_url'] = process.env.HOSTNAME + image.src_url;
      }
    }
  }

  return {
    props: {
      entities: entities,
    },
  };
}
