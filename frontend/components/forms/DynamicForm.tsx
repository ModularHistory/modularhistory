import axiosWithoutAuth from "@/axiosWithoutAuth";
import { InstantSearch } from "@/components/search/InstantSearch";
import {
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

interface DField {
  name: string;
  type:
    | "CharField"
    | "ManyRelatedField"
    | "ListField"
    | "HistoricDateTimeDrfField"
    | "PrimaryKeyRelatedField";
  editable: boolean;
  required: boolean;
  allowBlank: boolean;
  verboseName: string | null;
  helpText: string | null;
  choices: Record<string, any> | null;
  style: Record<string, any>;
  instantSearch?: {
    model: string;
    filters: Record<string, any>;
  };
}

//Dynamic fields form
//Can be called using the DynamicForm component or by using the DynamicFormFields prop and specifying the 'type' prop
const DynamicFormFields: FC<DynamicFormFieldsProps> = ({ contentType }: DynamicFormFieldsProps) => {
  const [formData, setFormData] = useState<DField[]>([]);

  const getDynamicFields = (contentType: string): Promise<DField[]> =>
    axiosWithoutAuth.get(`/api/${contentType}/fields/`).then((response) => response.data);

  const isLoading = useContext(PageTransitionContext);

  useEffect(() => {
    getDynamicFields(contentType).then((result) => {
      setFormData(result.filter((field) => field.editable));
    });
  }, [contentType]);

  // const checkField = (obj: any) => {
  //   return obj.editable;
  // };
  //
  const createDisplayName = (str: string) => {
    return str.replace(/_/g, " ");
  };
  //
  // const createChoiceValue = (str: string) => {
  //   return str.replace(/<.*?>/g, "");
  // };

  return (
    <>
      <Box component={"pre"} maxWidth={"80vw"}>
        {JSON.stringify(formData, null, 4)}
      </Box>
      <Grid container spacing={1}>
        {formData
          .map((field) => {
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
                />
              );
            }
            switch (field.type) {
              case "CharField":
                return (
                  <TextField
                    label={createDisplayName(field.name)}
                    variant="outlined"
                    helperText={field.helpText}
                    required={field.required}
                    sx={{ minWidth: "5rem" }}
                    multiline
                  />
                );
              default:
                return null;
            }
          })
          .map((field, index) => (
            <Grid item key={index}>
              {field}
            </Grid>
          ))}
      </Grid>
      <p>* = required field</p>
      <Button variant="contained" sx={{ m: "1rem" }} type="submit">
        Submit
      </Button>
    </>
  );
};

export default DynamicForm;
