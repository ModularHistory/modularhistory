import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import { Collection } from "@/types/modules";
import { CardContent } from "@mui/material";
// import Card from '@mui/material/Card';
import Grid from "@mui/material/Grid";
import { GetServerSideProps } from "next";
import Link from "next/link";
import { useState } from "react";
import { Card, Container } from "react-bootstrap";

// import styles from "assets/jss/nextjs-material-dashboard-pro/modalStyle.js";

interface CollectionProps {
  collectionsData: {
    results: Collection[];
    totalPages: number;
  };
}

const Collections: FC<CollectionProps> = ({ collectionsData }: CollectionProps) => {
  //Grid Component for collection card
  const collections = collectionsData["results"] || [];
  const collectionCards = collections.map((collection) => (
    <Grid item key={collection.slug} xs={6} sm={4} md={3}>
      <Link href={`/collections/${collection.slug}`}>
        <a>
          <Card>
            <CardContent>
              {collection.title}
              {collection.creator}
              {collection.entities}
              {/* {collection.propositions} */}
              {/* {/* {collection.quotes} */}
              {collection.sources}
            </CardContent>
          </Card>
        </a>
      </Link>
    </Grid>
  ));

  const [cards, setCards] = useState([]); // instantiate cards as an empty Array
  const [cardName, setName] = useState("");

  const addCard = () => {
    // create a new array with the old values and the new random one
    const newCards = [...cards, cardName];

    setCards(newCards);
    console.log(setCards);
  };

  // const removeCard = (cardIndex) => {
  //   // create a new array without the item that you are removing
  //   const newCards = cards.filter((card, index) => index !== cardIndex);

  //   setCards(newCards);
  // };

  return (
    <Layout title={"Collections"}>
      <PageHeader>Collections</PageHeader>
      {/* <div className="ui buttons" style={{ float: 'right' }}>
            <input 
              type="text" 
              name="Collection Name" 
              placeholder="Enter Collection Name..." 
              // value={ state.topicBox }
              onChange={ e => setName(e.target.value)} 
            />
            <Button color="primary" onClick={() => addCard()}> Add </Button>
            <div className="or mb-1 mt-1"></div>
          </div> */}
      <Pagination count={collectionsData["totalPages"]} />
      <Container>
        <Grid container spacing={2}>
          {collectionCards}
        </Grid>
      </Container>
    </Layout>
  );
};

export default Collections;

export const getServerSideProps: GetServerSideProps = async (context) => {
  let collectionsData = {};

  await axiosWithoutAuth
    .get("http://django:8000/api/collections/", { params: context.query })
    .then((response) => {
      collectionsData = response.data;
    });

  return {
    props: {
      collectionsData,
    },
  };
};

// export const CreateCollection = async (context) => {
//   let collectionsData = {};

//   await axiosWithoutAuth
//     .post("http://django:8000/api/collections/", { params: context.query })
//     .then((response) => {
//       collectionsData = response.data;
//     });

//   return {
//     props: {
//       collectionsData,
//     },
//   };
// };

// export default function Modal() {
//   const [modal, setModal] = useState(false);
//   const classes = useStyles();
//   const dialogClasses = {
//     root: center,
//     paper: modal
//   };
//   const [modalIsOpen,setIsOpen] = React.useState(false);
//   function openModal() {
//     setIsOpen(true);
//   }
// }
