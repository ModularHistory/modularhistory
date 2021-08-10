import axiosWithoutAuth from "@/axiosWithoutAuth";
import { fieldComponents } from "@/components/cms/fields";
import { ModelField } from "@/components/cms/fields/types";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { Proposition } from "@/interfaces";
import { Button, FormControl, Grid } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { GetServerSideProps } from "next";
import { Session } from "next-auth";
import { getSession, signIn } from "next-auth/client";
import { useRouter } from "next/router";
import React, { FC } from "react";

const useStyles = makeStyles({
  root: {},
  submitButton: {
    margin: "1rem",
  },
});

interface ModeratedProposition extends Proposition {
  fields: ModelField[];
}

interface PropositionProps {
  proposition: ModeratedProposition;
}

interface PropositionModificationPageProps extends PropositionProps {
  session: Session;
}

export const PropositionModificationForm: FC<PropositionProps> = ({
  proposition,
}: PropositionProps) => {
  const classes = useStyles();
  const handleSubmit = async (event) => {
    event.preventDefault();
  };
  return (
    <form method="post" onSubmit={handleSubmit} className={classes.root}>
      <div>
        {proposition.fields.map((field) => {
          const FieldComponent = fieldComponents[field.type];
          if (FieldComponent) {
            return (
              <FormControl fullWidth margin="normal">
                <FieldComponent key={field.name} value={proposition[field.name]} {...field} />
              </FormControl>
            );
          } else {
            console.log(`>>> ${field.name}: ${field.type}: ${proposition[field.name]}`);
            return null;
          }
        })}
      </div>
      <div style={{ textAlign: "center" }}>
        <Button type="submit" color="primary" variant="outlined" className={classes.submitButton}>
          {"Request review"}
        </Button>
      </div>
    </form>
  );
};

const PropositionModificationPage: FC<PropositionModificationPageProps> = ({
  proposition,
  session,
}: PropositionModificationPageProps) => {
  const router = useRouter();
  const baseUrl = typeof window !== "undefined" ? window.location.origin : "";
  // TODO
  if (!session?.user?.email) {
    signIn("github", { callbackUrl: `${baseUrl}/${router.asPath}` });
  }
  return (
    <Layout title={proposition.summary}>
      <PageHeader>Proposition {proposition.id}</PageHeader>
      <Grid container direction="row" justifyContent="space-evenly" alignItems="flex-start">
        <Grid item sm={12} md={6} lg={6} xl={6} style={{ margin: "0 3rem" }}>
          <PropositionModificationForm proposition={proposition} />
        </Grid>
      </Grid>
    </Layout>
  );
};
export default PropositionModificationPage;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  const session = await getSession(context);
  const { slug } = context.params;
  let proposition: ModeratedProposition;
  await axiosWithoutAuth
    .get(`http://django:8000/api/propositions/${slug}/moderation/`)
    .then((response) => {
      proposition = response.data;
    })
    .catch((error) => {
      console.log(error);
      proposition = null;
    });
  if (!proposition) {
    // https://nextjs.org/blog/next-10#notfound-support
    return {
      notFound: true,
    };
  }
  return {
    props: { proposition, session }, // passed to the page component as props
  };
};
