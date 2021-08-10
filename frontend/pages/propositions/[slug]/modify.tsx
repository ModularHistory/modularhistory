import axiosWithoutAuth from "@/axiosWithoutAuth";
import RichTextEditor from "@/components/cms/RichTextEditor";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { Proposition } from "@/interfaces";
import "@draft-js-plugins/inline-toolbar/lib/plugin.css";
import "@draft-js-plugins/static-toolbar/lib/plugin.css";
import { Button, FormControl, Grid, TextField, useTheme } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { ContentState, convertFromHTML, EditorState } from "draft-js";
import { GetServerSideProps } from "next";
import { Session } from "next-auth";
import { getSession, signIn } from "next-auth/client";
import { useRouter } from "next/router";
import React, { FC, useEffect, useState } from "react";

const useStyles = makeStyles({
  root: {},
  submitButton: {
    margin: "1rem",
  },
});

interface PropositionProps {
  proposition: Proposition;
}

interface PropositionModificationPageProps extends PropositionProps {
  session: Session;
}

export const PropositionModificationForm: FC<PropositionProps> = ({
  proposition,
}: PropositionProps) => {
  const theme = useTheme();
  const classes = useStyles(theme);
  const [title, setTitle] = useState(proposition.title);
  const [summary, setSummary] = useState(proposition.summary);
  const [elaborationEditorState, setElaborationEditorState] = useState(() =>
    EditorState.createEmpty()
  );
  useEffect(() => {
    const elaborationBlocksFromHtml = convertFromHTML(proposition.elaboration);
    const _elaborationState = ContentState.createFromBlockArray(
      elaborationBlocksFromHtml.contentBlocks,
      elaborationBlocksFromHtml.entityMap
    );
    setElaborationEditorState(EditorState.createWithContent(_elaborationState));
  }, []);
  const handleSubmit = async (event) => {
    event.preventDefault();
  };
  return (
    <form method="post" onSubmit={handleSubmit} className={classes.root}>
      {/* {error && <p className="text-center">{error}</p>} */}
      <FormControl fullWidth margin="dense">
        <TextField
          id="title"
          name="title"
          value={title}
          label={"Title"}
          onChange={(event) => setTitle(event.target.value)}
        />
      </FormControl>
      <FormControl fullWidth margin="dense">
        <TextField
          id="summary"
          name="summary"
          value={summary}
          label={"Summary"}
          onChange={(event) => setSummary(event.target.value)}
        />
      </FormControl>
      <div>
        <RichTextEditor editorState={elaborationEditorState} onChange={setElaborationEditorState} />
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
      <>
        <PageHeader>Proposition {proposition.id}</PageHeader>
        <Grid container direction="row" justifyContent="space-evenly" alignItems="flex-start">
          <Grid item sm={12} md={6} lg={6} xl={6} style={{ margin: "0 3rem" }}>
            <PropositionModificationForm proposition={proposition} />
          </Grid>
        </Grid>
      </>
    </Layout>
  );
};
export default PropositionModificationPage;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  const session = await getSession(context);
  const { slug } = context.params;
  let proposition: Proposition;
  await axiosWithoutAuth
    .get(`http://django:8000/api/propositions/${slug}/`)
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
