import axiosWithoutAuth from "@/axiosWithoutAuth";
import { TopicsInstantSearch } from "@/components/search/InstantSearch";
import {
  Box,
  Button,
  Card,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  TextField,
  Typography,
} from "@mui/material";
import { ParsedUrlQueryInput } from "querystring";
import { FC, MutableRefObject, useContext, useEffect, useRef, useState } from "react";
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

const fields = ["topics"] as const;
type Field = typeof fields[number];
type FieldsRef = MutableRefObject<Record<Field, any>>;
type FieldCallbacks = Record<Field, (value: ParsedUrlQueryInput[string]) => void>;

//Dynamic fields form
//Can be called using the DynamicForm component or by using the DynamicFormFields prop and specifying the 'type' prop
const DynamicFormFields: FC<DynamicFormFieldsProps> = ({ contentType }: DynamicFormFieldsProps) => {
  const [formData, setFormData] = useState([]);
  const [choiceValue, setChoiceValue] = useState<string[]>([]);

  const getDynamicFields = async (contentType: string) => {
    return await axiosWithoutAuth.get(`/api/${contentType}/fields/`).then((response) => {
      return response.data;
    });
  };

  const isLoading = useContext(PageTransitionContext);

  const handleChoice = (event: { target: { value: string[] | string } }) => {
    const value = event.target.value as string[] | string;
    setChoiceValue(typeof value === "string" ? value.split(",") : value);
  };

  const fieldsRef = useRef({}) as FieldsRef;
  const fieldCallbacks = Object.fromEntries(
    fields.map((name) => [name, (value: unknown) => (fieldsRef.current[name] = value)])
  ) as FieldCallbacks;

  useEffect(() => {
    getDynamicFields(contentType).then((result) => {
      setFormData(result);
    });
  }, [contentType]);

  const checkField = (obj: any) => {
    return obj.editable;
  };

  const createDisplayName = (str: string) => {
    return str.replace(/_/g, " ");
  };

  const createChoiceValue = (str: string) => {
    return str.replace(/<.*?>/g, "");
  };

  return (
    <>
      <FormControl>
        <Grid container spacing={3}>
          {formData &&
            formData.map((field: any) => (
              <>
                {checkField(field) &&
                  ((field.name === "tags" && (
                    <Grid item key={field.name} xs={4}>
                      <TopicsInstantSearch
                        label={"tags"}
                        onChange={fieldCallbacks.topics}
                        disabled={isLoading}
                        defaultValue={fieldsRef.current.topics}
                      />
                    </Grid>
                  )) ||
                    (field.type === "CharField" && (
                      <Grid item key={field.name} xs={4}>
                        <TextField
                          id={field.name}
                          label={createDisplayName(field.name)}
                          variant="outlined"
                          helperText={field.helpText}
                          required={field.required}
                          sx={{ minWidth: "5rem" }}
                        />
                      </Grid>
                    )) ||
                    (field.type === "ManyRelatedField" && (
                      <Grid item key={field.name} xs={4}>
                        <FormControl>
                          <InputLabel id={field.name}>{createDisplayName(field.name)}</InputLabel>
                          <Select
                            labelId={field.name}
                            id={field.name}
                            label={createDisplayName(field.name)}
                            value={choiceValue}
                            required={field.required}
                            multiple
                            autoWidth
                            variant="outlined"
                            onChange={handleChoice}
                            input={<OutlinedInput label={createDisplayName(field.name)} />}
                            sx={{ width: "10rem" }}
                            MenuProps={{
                              anchorOrigin: { vertical: "bottom", horizontal: "center" },
                              style: { width: "30rem" },
                            }}
                          >
                            {field.choices &&
                              Object.values(field.choices).map((choice: any) => (
                                <MenuItem key={choice} value={choice} dense divider>
                                  <Typography noWrap>{createChoiceValue(choice)}</Typography>
                                </MenuItem>
                              ))}
                          </Select>
                        </FormControl>
                      </Grid>
                    )))}
              </>
            ))}
        </Grid>
        <p>* = required field</p>
        <Button variant="contained" sx={{ m: "1rem" }} type="submit">
          Submit
        </Button>
      </FormControl>
    </>
  );
};

export default DynamicForm;
