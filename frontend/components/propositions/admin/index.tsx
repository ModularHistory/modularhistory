import { FC } from "react";
import { Datagrid, List, ListProps, TextField } from "react-admin";
import { PropositionCreate, PropositionEdit } from "./Edit";

export const PropositionList: FC<ListProps> = (props: ListProps) => (
  <List {...props} title="Propositions">
    <Datagrid>
      <TextField source="summary" />
      <TextField source="slug" />
    </Datagrid>
  </List>
);

const propositions = {
  list: PropositionList,
  create: PropositionCreate,
  edit: PropositionEdit,
};

export default propositions;
