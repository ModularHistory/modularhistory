import { FC } from "react";
import { Datagrid, List, ListProps, TextField } from "react-admin";
import { SourceCreate, SourceEdit } from "./Edit";

export const SourceList: FC<ListProps> = (props: ListProps) => (
  <List {...props} title="Sources">
    <Datagrid>
      <TextField source="citationHtml" label="Citation HTML" />
      <TextField source="slug" />
    </Datagrid>
  </List>
);

const sources = {
  list: SourceList,
  create: SourceCreate,
  edit: SourceEdit,
};

export default sources;
