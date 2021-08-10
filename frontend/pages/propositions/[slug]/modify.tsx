import axiosWithoutAuth from "@/axiosWithoutAuth";
import RichTextEditor from "@/components/cms/RichTextEditor";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { Proposition } from "@/interfaces";
import "@draft-js-plugins/inline-toolbar/lib/plugin.css";
import "@draft-js-plugins/static-toolbar/lib/plugin.css";
import {
  Button,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  TextField,
  useTheme,
} from "@material-ui/core";
import Checkbox from "@material-ui/core/Checkbox";
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

interface ModelField {
  name: string;
  verboseName: string;
  editable: boolean;
  type: string;
}

interface ModeratedProposition extends Proposition {
  fields: ModelField[];
}

interface PropositionProps {
  proposition: ModeratedProposition;
}

interface PropositionModificationPageProps extends PropositionProps {
  session: Session;
}

interface FieldProps {
  name: string;
  verboseName: string;
  editable?: boolean;
}

interface BooleanFieldProps extends FieldProps {
  value?: boolean;
}

interface TextFieldProps extends FieldProps {
  value?: string;
}

interface CharFieldProps extends TextFieldProps {
  choices?: string[][]; // [["value", "Human-readable value"], ["a", "A"]]
}

const HTMLField: FC<TextFieldProps> = ({ value }: TextFieldProps) => {
  const [editorState, setEditorState] = useState(() => EditorState.createEmpty());
  useEffect(() => {
    const blocksFromHtml = convertFromHTML(value);
    const _state = ContentState.createFromBlockArray(
      blocksFromHtml.contentBlocks,
      blocksFromHtml.entityMap
    );
    setEditorState(EditorState.createWithContent(_state));
  }, [value]);
  return <RichTextEditor editorState={editorState} onChange={setEditorState} />;
};

const CharField: FC<CharFieldProps> = (props: CharFieldProps) => {
  const [value, setValue] = useState(props.value);
  if (props.choices) {
    return (
      <TextField
        id={props.name}
        name={props.name}
        value={value}
        label={props.verboseName}
        onChange={(event) => setValue(event.target.value)}
        select
      >
        {props.choices.map((choice) => (
          <MenuItem key={choice[0]}>{choice[1]}</MenuItem>
        ))}
      </TextField>
    );
  } else {
    return (
      <TextField
        id={props.name}
        name={props.name}
        value={value}
        label={props.verboseName}
        onChange={(event) => setValue(event.target.value)}
        disabled={props.editable === false}
      />
    );
  }
};

const BooleanField: FC<BooleanFieldProps> = (props: BooleanFieldProps) => {
  const [value, setValue] = useState(props.value);
  return (
    <FormControl>
      <InputLabel htmlFor={props.name}>{props.verboseName}</InputLabel>
      <Checkbox
        id={props.name}
        checked={value === true}
        disabled={props.editable === false}
        onChange={(event) => setValue(event.target.checked)}
      />
    </FormControl>
  );
};

const fieldComponents = {
  ManyToManyRel: undefined,
  ManyToOneRel: undefined,
  OneToOneRel: undefined,
  AutoField: undefined,
  AutuSlugField: undefined,
  HistoricDateTimeField: undefined,
  BooleanField: BooleanField,
  HTMLField: HTMLField,
  CharField: CharField,
  PostitiveSmallIntegerField: undefined,
  SourcesField: undefined,
  ImagesField: undefined,
  LocationsField: undefined,
  RelatedQuotesField: undefined,
  GenericRelation: undefined,
};

export const PropositionModificationForm: FC<PropositionProps> = ({
  proposition,
}: PropositionProps) => {
  const theme = useTheme();
  const classes = useStyles(theme);
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
              <FormControl fullWidth margin="dense">
                <FieldComponent key={field.name} value={proposition[field.name]} {...field} />
              </FormControl>
            );
          } else {
            console.log(`>>> ${field.name}: ${field.type}`);
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
