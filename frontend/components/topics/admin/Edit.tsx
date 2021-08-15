import { FC } from "react";
import {
  Create,
  CreateProps,
  Datagrid,
  DateField,
  DateInput,
  Edit,
  EditButton,
  EditProps,
  ReferenceManyField,
  required,
  SimpleForm,
  TextField,
  TextInput,
} from "react-admin";

export const TopicCreate: FC<CreateProps> = (props: CreateProps) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="name" />
    </SimpleForm>
  </Create>
);

export const TopicEdit: FC<EditProps> = (props: EditProps) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput disabled label="ID" source="id" />
      <TextInput source="name" validate={required()} />
      <DateInput label="Publication date" source="published_at" />
      <ReferenceManyField label="Comments" reference="comments" target="post_id">
        <Datagrid>
          <TextField source="body" />
          <DateField source="created_at" />
          <EditButton />
        </Datagrid>
      </ReferenceManyField>
    </SimpleForm>
  </Edit>
);
