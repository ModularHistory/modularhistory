import { TextFieldProps } from "@/components/cms/fields/types";
import RichTextEditor from "@/components/cms/RichTextEditor";
import "@draft-js-plugins/inline-toolbar/lib/plugin.css";
import "@draft-js-plugins/static-toolbar/lib/plugin.css";
import { ContentState, convertFromHTML, EditorState } from "draft-js";
import React, { FC, useEffect, useState } from "react";

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

export default HTMLField;
