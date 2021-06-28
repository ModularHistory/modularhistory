import { FC } from "react";
import { Datagrid, DateField, List, ListProps, TextField } from "react-admin";
import { EntityCreate, EntityEdit } from "./Edit";

export const EntityList: FC<ListProps> = (props: ListProps) => (
  <List {...props}>
    <Datagrid>
      <TextField source="name" />
      <TextField source="aliases" />
      <DateField source="birthDate" />
      <DateField source="deathDate" />
      <TextField source="type" />
    </Datagrid>
  </List>
);

const entities = {
  list: EntityList,
  create: EntityCreate,
  edit: EntityEdit,
};

export default entities;
