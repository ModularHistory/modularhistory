import axiosWithoutAuth from "@/axiosWithoutAuth";
import { InstantSearch } from "@/components/search/InstantSearch";
import YearSelect from "@/components/search/YearSelect";
import {
  Autocomplete,
  Box,
  Button,
  Card,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  TextFieldProps,
} from "@mui/material";
import { FC, useContext, useEffect, useState } from "react";
import PageTransitionContext from "../PageTransitionContext";

const DynamicForm: FC = () => {
  const [contentType, setContentType] = useState("");

  const handleContentTypeChange = (event: { target: { value: string } }) => {
    setContentType(event.target.value);
  };

  return (
    <Card raised>
      <FormControl sx={{ minWidth: "20rem", m: "1rem" }}>
        <InputLabel id="select-form-type">Type of Content</InputLabel>
        <Select
          labelId="select-form-type"
          id="select-form"
          value={contentType}
          label="Type of Content"
          onChange={handleContentTypeChange}
        >
          <MenuItem value={"none"}>
            <em>None</em>
          </MenuItem>
          <MenuItem value={"quotes"}>Quote</MenuItem>
          <MenuItem value={"entities"}>Entity</MenuItem>
          <MenuItem value={"images"}>Image</MenuItem>
          <MenuItem value={"occurrences"}>Occurrence</MenuItem>
          <MenuItem value={"propositions"}>Proposition</MenuItem>
          <MenuItem value={"topics"}>Topic</MenuItem>
        </Select>
      </FormControl>
      {contentType && contentType != "none" && (
        <>
          <Divider sx={{ borderBottomWidth: 2 }} />
          <Box
            sx={{
              flex: "1 1",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "1.5rem 1rem 1.5rem 1rem",
            }}
          >
            <Box>
              <DynamicFormFields contentType={contentType} />
            </Box>
          </Box>
        </>
      )}
    </Card>
  );
};

interface DynamicFormFieldsProps {
  contentType: string;
}

interface Field {
  name: string;
  type:
    | "CharField"
    | "ManyRelatedField"
    | "ListField"
    | "HistoricDateTimeField"
    | "PrimaryKeyRelatedField";
  editable: boolean;
  required: boolean;
  allowBlank: boolean | null;
  verboseName: string | null;
  helpText: string | null;
  choices: Record<string, string> | null;
  style: Record<string, any>;
  instantSearch?: {
    model: string;
    filters: Record<string, any>;
  };
}

//Dynamic fields form
//Can be called using the DynamicForm component or by using the DynamicFormFields prop and specifying the 'type' prop
const DynamicFormFields: FC<DynamicFormFieldsProps> = ({ contentType }: DynamicFormFieldsProps) => {
  const [fields, setFields] = useState<{ required: Field[]; optional: Field[] }>({
    required: [],
    optional: [],
  });

  const getDynamicFields = (contentType: string): Promise<Field[]> =>
    axiosWithoutAuth.get(`/api/${contentType}/fields/`).then((response) => response.data);

  const isLoading = useContext(PageTransitionContext);

  useEffect(() => {
    getDynamicFields(contentType).then((result) => {
      const editableFields = result.filter((field) => field.editable);
      setFields({
        required: editableFields.filter((field) => field.required),
        optional: editableFields.filter((field) => !field.required),
      });
    });
  }, [contentType]);

  // const checkField = (obj: any) => {
  //   return obj.editable;
  // };
  //
  //
  // const createChoiceValue = (str: string) => {
  //   return str.replace(/<.*?>/g, "");
  // };

  return (
    <>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Divider textAlign={"left"} sx={{ mb: 2 }}>
            <b>Required</b>
          </Divider>
        </Grid>
        {fields.required.map((field, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <DynamicField field={field} />
          </Grid>
        ))}
        <Grid item xs={12}>
          <Divider textAlign={"left"} sx={{ mb: 2 }}>
            <b>Optional</b>
          </Divider>
        </Grid>
        {fields.optional.map((field, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <DynamicField field={field} />
          </Grid>
        ))}
      </Grid>
      <p>* = required field</p>
      <Button variant="contained" sx={{ m: "1rem" }} type="submit">
        Submit
      </Button>
      <Box component={"pre"} maxWidth={"80vw"}>
        {JSON.stringify(fields, null, 4)}
      </Box>
    </>
  );
};

const DynamicField: FC<{ field: Field }> = ({ field }) => {
  const commonProps: TextFieldProps = {
    required: field.required && !(field.type === "CharField" && field.allowBlank),
    label: createDisplayName(field.name),
    helperText: field.helpText,
    variant: "outlined",
    fullWidth: true,
  };
  if (field.instantSearch) {
    return (
      <InstantSearch
        label={field.name}
        getDataForInput={(input) =>
          axiosWithoutAuth
            .get(`/api/search/instant/`, {
              params: { model: field.instantSearch?.model, query: input },
            })
            .then(({ data }) => data)
        }
        labelKey={"name"}
        multiple={field.type === "ManyRelatedField"}
      />
    );
  }
  switch (field.type) {
    case "CharField":
      return <TextField {...commonProps} sx={{ minWidth: "5rem" }} multiline />;
    case "ListField":
      return (
        <Autocomplete
          multiple
          id="tags-filled"
          freeSolo
          options={[]}
          renderInput={(params) => <TextField {...params} {...commonProps} />}
        />
      );
    case "PrimaryKeyRelatedField":
      return (
        <TextField {...commonProps} select sx={{ minWidth: "5rem" }}>
          {Object.entries(field.choices ?? {}).map(([id, choice]) => (
            <MenuItem value={id} key={id}>
              <span dangerouslySetInnerHTML={{ __html: choice }} />
            </MenuItem>
          ))}
        </TextField>
      );
    case "HistoricDateTimeField":
      return <YearSelect />;
    default:
      ((field: never) => {
        console.error(`Unexpected field type encountered: ${field}`);
      })(field);
      return <p>Unrendered: {field.name}</p>;
  }
};

const createDisplayName = (str: string) => {
  return str.replace(/_/g, " ");
};

export default DynamicForm;
