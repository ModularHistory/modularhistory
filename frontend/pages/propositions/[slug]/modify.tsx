import axiosWithoutAuth from "@/axiosWithoutAuth";
import RichTextEditor from "@/components/cms/RichTextEditor";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { Proposition } from "@/interfaces";
import "@draft-js-plugins/inline-toolbar/lib/plugin.css";
import "@draft-js-plugins/static-toolbar/lib/plugin.css";
import { Button, FormControl, Grid, TextField, useTheme } from "@material-ui/core";
import EditIcon from "@material-ui/icons/Edit";
import { makeStyles } from "@material-ui/styles";
import { ContentState, convertFromHTML, EditorState } from "draft-js";
import { GetStaticPaths, GetStaticProps } from "next";
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
          {"Create pull request"}
        </Button>
      </div>
    </form>
  );
};

const PropositionModificationPage: FC<PropositionProps> = ({ proposition }: PropositionProps) => {
  return (
    <Layout title={proposition.summary}>
      <PageHeader>Proposition {proposition.id}</PageHeader>
      <Grid container direction="row" justifyContent="space-evenly" alignItems="flex-start">
        <Grid item sm={12} md={6} lg={6} xl={6} style={{ margin: "0 3rem" }}>
          <a
            href={`https://github.com/ModularHistory/content/tree/main/propositions/${proposition.id}.toml`}
            rel="noreferrer"
            target="_blank"
          >
            <EditIcon style={{ float: "right", margin: "1rem" }} />
          </a>
          <PropositionModificationForm proposition={proposition} />
        </Grid>
      </Grid>
    </Layout>
  );
};
export default PropositionModificationPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let proposition: Proposition;
  const { slug } = params;
  const body = {
    query: `{
      proposition(slug: "${slug}") {
        id
        title
        summary
        elaboration
        model
        adminUrl
        certainty
        arguments {
          pk
          type
          explanation
          premises {
            absoluteUrl
            dateString
            certainty
            slug
            summary
            elaboration
          }
        }
        conflictingPropositions {
          slug
          absoluteUrl
          summary
          certainty
        }
        pullRequests {
          url
        }
      }
    }`,
  };
  await axiosWithoutAuth
    .post("http://django:8000/graphql/", body)
    .then((response) => {
      proposition = response.data.data.proposition;
    })
    .catch(() => {
      proposition = null;
    });

  if (!proposition) {
    // https://nextjs.org/blog/next-10#notfound-support
    return {
      notFound: true,
    };
  }
  return {
    props: {
      proposition,
    },
    revalidate: 10,
  };
};

export const getStaticPaths: GetStaticPaths = async () => {
  return {
    paths: [],
    fallback: "blocking",
  };
};
