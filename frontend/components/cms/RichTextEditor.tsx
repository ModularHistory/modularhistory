import Editor from "@draft-js-plugins/editor";
import createInlineToolbarPlugin from "@draft-js-plugins/inline-toolbar";
import "@draft-js-plugins/inline-toolbar/lib/plugin.css";
import createToolbarPlugin from "@draft-js-plugins/static-toolbar";
import "@draft-js-plugins/static-toolbar/lib/plugin.css";
import { makeStyles } from "@material-ui/styles";
import React, { Dispatch, FC, useMemo, useRef } from "react";

const useStyles = makeStyles({
  root: {
    border: "1px solid lightgray",
    borderRadius: "2px",
    padding: "1rem",
  },
});

interface RichTextEditorProps {
  editorState: boolean;
  onChange: Dispatch<any>;
}

const RichTextEditor: FC<RichTextEditorProps> = ({
  editorState,
  onChange,
}: RichTextEditorProps) => {
  const classes = useStyles();
  const toolbarPlugin = createToolbarPlugin();
  const { Toolbar } = toolbarPlugin;
  const [plugins, InlineToolbar] = useMemo(() => {
    const inlineToolbarPlugin = createInlineToolbarPlugin();
    return [[toolbarPlugin, inlineToolbarPlugin], inlineToolbarPlugin.InlineToolbar];
  }, []);
  const editor = useRef<Editor | null>(null);
  return (
    <div className={classes.root}>
      <Editor
        editorState={editorState}
        onChange={onChange}
        plugins={plugins}
        ref={(element) => {
          editor.current = element;
        }}
      />
      <InlineToolbar />
      <Toolbar />
    </div>
  );
};

export default RichTextEditor;
