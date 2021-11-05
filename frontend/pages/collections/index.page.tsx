import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import Pagination from "@/components/Pagination";
import { Collection } from "@/types/modules";
import { CardContent } from "@mui/material";
import Autocomplete, { createFilterOptions } from "@mui/material/Autocomplete";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Grid from "@mui/material/Grid";
import TextField from "@mui/material/TextField";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import Link from "next/link";
import { FC, useState } from "react";
import { Card, Container } from "react-bootstrap";
interface CollectionProps {
  collectionsData: {
    results: Collection[];
    totalPages: number;
  };
}

const filter = createFilterOptions();

const Collections: FC<CollectionProps> = ({ collectionsData }: CollectionProps) => {
  //Grid Component for collection card
  const collections = collectionsData["results"] || [];
  const collectionCards = collections.map((collection) => (
    <Grid item key={collection.slug} xs={6} sm={4} md={3}>
      <Link href={`/collections/${collection.slug}`}>
        <a>
          <Card>
            <CardContent>{collection.title}</CardContent>
          </Card>
        </a>
      </Link>
    </Grid>
  ));

  const [value, setValue] = useState<string | null>(null);
  const [open, toggleOpen] = useState(false);

  const handleClose = () => {
    setDialogValue({
      key: "",
    });

    toggleOpen(false);
  };

  const [dialogValue, setDialogValue] = useState({
    key: "",
  });

  const handleSubmit = (event: Event) => {
    event.preventDefault();
    setValue(dialogValue.key);

    handleClose();
  };

  return (
    <Layout>
      <NextSeo
        title={"Collections"}
        canonical={"/collections"}
        description={
          "Browse collections of historical occurrences, entities, sources, and more related to your topics of interest."
        }
      />
      <Autocomplete
        value={value}
        onChange={(event, newValue) => {
          if (typeof newValue === "string") {
            // timeout to avoid instant validation of the dialog's form.
            setTimeout(() => {
              toggleOpen(true);
              setDialogValue({
                key: newValue,
              });
            });
          }
        }}
        filterOptions={(options, params) => {
          const filtered = filter(options, params);

          if (params.inputValue !== "") {
            filtered.push({
              inputValue: params.inputValue,
              title: `Add "${params.inputValue}"`,
            });
          }

          return filtered;
        }}
        //   renderInput={params => (
        //     <TextField {...params} label="Label" variant="outlined" fullWidth />
        // )}
        id="free-solo-dialog-demo"
        options={collectionCards}
        getOptionLabel={(option) => {
          // e.g value selected with enter, right from the input
          if (typeof option === "string") {
            // console.log(option)
            return option;
          }
          if (option.inputValue) {
            // console.log(option.inputValue)
            return option.inputValue;
          }
          console.log(option.key);
          return option.key;
        }}
        selectOnFocus
        clearOnBlur
        handleHomeEndKeys
        renderOption={(props, option) => <li {...props}>{option.key}</li>}
        sx={{ width: 300 }}
        freeSolo
        renderInput={(params) => <TextField {...params} label="Collections..." />}
      />
      <Dialog open={open} onClose={handleClose}>
        <form onSubmit={handleSubmit}>
          <DialogTitle>Add a new collection</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              id="name"
              value={dialogValue.key}
              onChange={(event) =>
                setDialogValue({
                  ...dialogValue,
                  key: event.target.value,
                })
              }
              label="title"
              type="text"
              variant="standard"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button type="submit">Add</Button>
          </DialogActions>
        </form>
      </Dialog>
      <PageHeader>Collections</PageHeader>
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
