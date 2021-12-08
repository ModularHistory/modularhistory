import {
  BlockquoteButton,
  BoldButton,
  CodeButton,
  HeadlineOneButton,
  HeadlineThreeButton,
  HeadlineTwoButton,
  ItalicButton,
  OrderedListButton,
  UnderlineButton,
  UnorderedListButton,
} from "@draft-js-plugins/buttons";
import Editor from "@draft-js-plugins/editor";
import createLinkifyPlugin from "@draft-js-plugins/linkify";
import createToolbarPlugin, { Separator } from "@draft-js-plugins/static-toolbar";
import { ToolbarChildrenProps } from "@draft-js-plugins/static-toolbar/lib/components/Toolbar";
import "@draft-js-plugins/static-toolbar/lib/plugin.css";
import { RawOff, RawOn } from "@mui/icons-material";
import { Box } from "@mui/material";
import { ContentState, EditorState, RichUtils } from "draft-js";
import { stateToHTML } from "draft-js-export-html";
import { stateFromHTML } from "draft-js-import-html";
import "draft-js/dist/Draft.css";
import { FC, useCallback, useEffect, useRef, useState } from "react";
import toolbarStyles from "./toolbarStyles.module.css";

const HTMLEditor = () => {
  const [editorState, setEditorState] = useState(() => EditorState.createEmpty());
  const [{ plugins, Toolbar }] = useState(() => {
    const toolbarPlugin = createToolbarPlugin({
      theme: {
        toolbarStyles: toolbarStyles,
        buttonStyles: toolbarStyles,
      },
    });
    const linkifyPlugin = createLinkifyPlugin();
    const { Toolbar } = toolbarPlugin;
    const plugins = [toolbarPlugin, linkifyPlugin];
    return {
      plugins,
      Toolbar,
    };
  });

  const editorRef = useRef<any>(null);
  useEffect(() => {
    console.log({ editorRef: editorRef.current });
  }, [editorRef.current]);

  return (
    <Box
      display={"flex"}
      flexDirection={"column-reverse"}
      boxSizing={"border-box"}
      border={"1px solid #ddd"}
      padding={"16px"}
      borderRadius={"2px"}
      marginBottom={"2em"}
      boxShadow={"inset 0px 1px 8px -3px #ABABAB"}
      bgcolor={"#FEFEFE"}
      sx={{
        cursor: "text",
        "& .DraftEditor-root": {
          minHeight: 40,
          hyphens: "auto",
          wordBreak: "break-word",
        },
        "& svg": {
          overflow: "revert",
          verticalAlign: "revert",
        },
      }}
    >
      <Editor
        editorState={editorState}
        onChange={setEditorState}
        plugins={plugins}
        ref={editorRef}
      />
      <Box mb={2}>
        <Toolbar>
          {(externalProps) => (
            <>
              <BoldButton {...externalProps} />
              <ItalicButton {...externalProps} />
              <UnderlineButton {...externalProps} />
              <CodeButton {...externalProps} />
              <Separator />
              <HeadlinesButton {...externalProps} />
              <UnorderedListButton {...externalProps} />
              <OrderedListButton {...externalProps} />
              <BlockquoteButton {...externalProps} />
              {/* We need custom HTML conversion before we can use raw HTML editing */}
              {/*<RawButton {...externalProps} />*/}
            </>
          )}
        </Toolbar>
      </Box>
    </Box>
  );
};

const RawButton: FC<ToolbarChildrenProps> = (props) => {
  const { getEditorState, setEditorState, onOverrideContent, theme } = props;
  const editorState = getEditorState();

  const handleClick = () => {
    onOverrideContent((props) => (
      <Box ml={"auto"}>
        <Separator />
        <Box className={theme.buttonWrapper}>
          <button
            className={theme.button}
            onClick={() => {
              setEditorState(
                EditorState.createWithContent(
                  stateFromHTML(getEditorState().getCurrentContent().getPlainText(), {})
                )
              );
              onOverrideContent(undefined);
            }}
          >
            <RawOff />
          </button>
        </Box>
      </Box>
    ));
    setEditorState(
      EditorState.createWithContent(
        ContentState.createFromText(stateToHTML(editorState.getCurrentContent()))
      )
    );
  };

  return (
    <Box ml={"auto"}>
      <Separator />
      <Box className={props.theme.buttonWrapper} fontSize={"12px"}>
        <button className={props.theme.button} onClick={handleClick}>
          <RawOn />
        </button>
      </Box>
    </Box>
  );
};

const HeadlinesPicker: FC<ToolbarChildrenProps> = (props) => {
  useEffect(() => {
    const handleWindowClick = () => {
      props.onOverrideContent(undefined);
    };
    setTimeout(() => {
      window.addEventListener("click", handleWindowClick);
    });
    return () => {
      window.removeEventListener("click", handleWindowClick);
    };
  }, [props]);
  console.log("render");

  const buttons = [HeadlineOneButton, HeadlineTwoButton, HeadlineThreeButton];

  return (
    <Box>
      {buttons.map((Button, i) => (
        <Button key={i} {...props} />
      ))}
    </Box>
  );
};

const HeadlinesButton: FC<ToolbarChildrenProps> = (props) => {
  // Allow `theme` to be passed, since `onOverrideContent` drops it.
  const HeadlinesPickerMemoized = useCallback(
    (pickerProps) => <HeadlinesPicker theme={props.theme} {...pickerProps} />,
    [props.theme]
  );

  const handleClick = () => {
    props.onOverrideContent(HeadlinesPickerMemoized);
  };

  const editorState = props.getEditorState();

  return (
    <Box className={props.theme.buttonWrapper}>
      <button
        className={
          (props.theme.button ?? "") +
          (RichUtils.getCurrentBlockType(editorState).startsWith("header")
            ? ` ${props.theme.active}`
            : "")
        }
        onClick={handleClick}
      >
        <strong>H</strong>
      </button>
    </Box>
  );
};

export default HTMLEditor;
