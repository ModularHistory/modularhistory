import { FC } from "react";
import { Datagrid, List, ListProps, TextField } from "react-admin";
import { ImageCreate, ImageEdit } from "./Edit";

export const ImageList: FC<ListProps> = (props: ListProps) => (
  <List {...props} title="Images">
    <Datagrid>
      <TextField source="captionHtml" label="Caption HTML" />
      <TextField source="slug" />
    </Datagrid>
  </List>
);

const images = {
  list: ImageList,
  create: ImageCreate,
  edit: ImageEdit,
};

export default images;
