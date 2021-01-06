import Head from "next/head";
import Link from "next/link";
import axios from "axios";

import Container from "@material-ui/core/Container"
import Grid from "@material-ui/core/Grid"
import Card from "@material-ui/core/Card";
import CardHeader from "@material-ui/core/CardHeader";
import CardMedia from "@material-ui/core/CardMedia";
import CardContent from "@material-ui/core/CardContent";

import Pagination from "@material-ui/lab/Pagination"
import PaginationItem from '@material-ui/lab/PaginationItem';

import Layout from "../../components/layout";

import {useRouter} from "next/router";
import {useState} from "react";

function PaginationLink({href, ...childProps}) {
  return (
    <Link href={href}>
      <a {...childProps}/>
    </Link>
  );
}

export default function Entities({entitiesData}) {
  const entities = entitiesData['results'];
  const router = useRouter();
  const isLastPage = entitiesData['next'] === null;
  const pageNum = Number(router.query['page'] || 1);

  const [pageCount,] = useState(() => (
    isLastPage
      ? pageNum
      : Math.ceil(entitiesData['count'] / entities.length)
  ));

  const pagination = (
    <Pagination
      count={pageCount} page={pageNum}
      variant="outlined" shape="rounded"
      renderItem={(item) => (
        <PaginationItem
          {...item} component={PaginationLink}
          href={item.page !== 1 ? `?page=${item.page}` : router.pathname}
        />
      )}
    />
  );

  const entityCards = entities.map(entity => (
    <Grid item key={entity['pk']}
          xs={10} sm={4} md={3}>
      <Card>
        <CardHeader title={entity['name']}/>
        {entity['serialized_images'].length > 0 &&
        <CardMedia
          component={'img'}
          src={entity['serialized_images'][0]['src_url']}
        />
        }
        <CardContent
          dangerouslySetInnerHTML={{__html: entity.description}}
        />
      </Card>
    </Grid>
  ));

  return (
    <Layout title={"Entities"}>
      <Container>
        <Grid container spacing={2}>
          <Grid item xs={10}>
            {pagination}
          </Grid>
          {entityCards}
        </Grid>
      </Container>
      {/*<pre>{JSON.stringify(entitiesData, null, 4)}</pre>*/}
    </Layout>
  );
}


export async function getServerSideProps(context) {
  const q = context.query;
  console.log(`requesting entities from DRF (page=${q['page']})`);
  const entitiesReq = await axios.get(
    "http://drf:8001/entities/api/" +
    ('page' in q ? `?page=${q['page']}` : "")
  );
  console.log("received entities from DRF");
  // TODO: catch errors

  return {
    props: {
      entitiesData: entitiesReq.data,
    },
  };
}
