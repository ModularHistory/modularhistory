import axiosWithAuth from "@/axiosWithAuth";
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
import { useSession } from "next-auth/client";
import { NextSeo } from "next-seo";
import Link from "next/link";
import React, { FC, useState } from "react";
import { Card, Container } from "react-bootstrap";

interface CollectionProps {
  collectionsData: {
    results: Collection[];
    totalPages: number;
  };
}

const filter = createFilterOptions<Option>();
type Option = Pick<Collection, "title"> & Partial<Collection> & { isOpen?: boolean };

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
  return (
    <Layout>
      <NextSeo
        title={"Collections"}
        canonical={"/collections"}
        description={
          "Browse collections of historical occurrences, entities, sources, and more related to your topics of interest."
        }
      />
      <PageHeader>Collections</PageHeader>
      <DisplayCard collections={collections}></DisplayCard>
      <Pagination count={collectionsData["totalPages"]} />
      <Container>
        <Grid container spacing={2}>
          {collectionCards}
        </Grid>
      </Container>
    </Layout>
  );
};

//Autocomplete Component
const DisplayCard: FC<{ collections: Collection[] }> = ({ collections }) => {
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

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setValue(dialogValue.key);
    saveCollection(dialogValue.key);
    handleClose();
  };

  const [session, loading] = useSession();

  const saveCollection = async (event: string) => {
    const title = event;
    const creator = session?.user?.handle;
    const slug = title.replace(/ /g, "-");
    console.log("The log is", title, creator, slug);

    const data = JSON.stringify({
      title: title,
      creator: creator,
      slug: slug,
    });

    await axiosWithAuth
      .post(
        "/api/collections/",
        { headers: { "Content-Type": "application/json" } },
        { data: data }
      )
      .then(function (response) {
        console.log(JSON.stringify(response.data));
      })
      .catch(function (error) {
        console.log(error);
      });
  };

  return (
    <div>
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
          } else if (newValue && newValue.title) {
            toggleOpen(true);
            setDialogValue({
              key: newValue.title,
            });
          } else {
            setValue(value);
          }
        }}
        filterOptions={(options, params) => {
          const filtered = filter(options, params);
          if (params.inputValue !== "") {
            filtered.push({
              title: `Add "${params.inputValue}"`,
              isOpen: true,
            });
          }
          return filtered;
        }}
        id="free-solo-dialog-demo"
        options={collections as Option[]}
        getOptionLabel={(option) => {
          if (typeof option === "string") {
            // console.log("The option is",option)
            return option;
          }
          return option.title ?? option.slug;
        }}
        selectOnFocus
        clearOnBlur
        handleHomeEndKeys
        renderOption={(props, option) => {
          if (option.isOpen === true) {
            return <li {...props}>{option.title}</li>;
          }
          const { onClick, ...otherProps } = props; //eslint-disable-line @typescript-eslint/no-unused-vars
          return (
            <Link href={`/collections/${option.slug}`} passHref>
              <li {...otherProps}>{option.title}</li>
            </Link>
          );
        }}
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
    </div>
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
