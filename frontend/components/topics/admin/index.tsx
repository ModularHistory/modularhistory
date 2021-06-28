import { FC } from "react";
import { Datagrid, List, ListProps, TextField } from "react-admin";
import { TopicCreate, TopicEdit } from "./Edit";

export const TopicList: FC<ListProps> = (props: ListProps) => (
  <List {...props} title="Topics">
    <Datagrid>
      <TextField source="name" />
    </Datagrid>
  </List>
);

const images = {
  list: TopicList,
  create: TopicCreate,
  edit: TopicEdit,
};

export default images;
