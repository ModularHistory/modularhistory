import axiosWithoutAuth from "@/axiosWithoutAuth";
import {
  Box,
  Button,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
} from "@mui/material";
import Card from "@mui/material/Card";
import TextField from "@mui/material/TextField";
import { FC, useEffect, useState } from "react";

const DyanmicForm: FC = () => {
  const [type, setType] = useState("");

  const handleFormType = (event: { target: { value: string } }) => {
    setType(event.target.value);
  };

  return (
    <Card elevation={5}>
      <FormControl sx={{ minWidth: "20rem", m: "1rem" }}>
        <InputLabel id="select-form-type">Type of Content</InputLabel>
        <Select
          labelId="select-form-type"
          id="select-form"
          value={type}
          label="Type of Content"
          onChange={handleFormType}
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
      {type && type != "none" && (
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
              <DyanmicFormFields type={type} />
            </Box>
          </Box>
        </>
      )}
    </Card>
  );
};

interface DyanmicFormProps {
  type: string;
}

//Dynamic fields form
//Can be called using the DyanmicForm component or by using the DynamicFormFields prop and specifying the 'type' prop
const DyanmicFormFields: FC<DyanmicFormProps> = ({ type }: DyanmicFormProps) => {
  const [formData, setFormData] = useState([]);
  const [choiceValue, setChoiceValue] = useState<string[]>([]);

  const getDyanmicFields = async (type: string) => {
    return await axiosWithoutAuth.get(`/api/${type}/fields/`).then((response) => {
      return response.data;
    });
  };

  const handleChoice = (event: { target: { value: string[] | string } }) => {
    const value = event.target.value as string[] | string;
    setChoiceValue(typeof value === "string" ? value.split(",") : value);
  };

  useEffect(() => {
    getDyanmicFields(type).then((result) => {
      setFormData(result);
    });
  });

  const checkField = (obj: any) => {
    return obj.editable;
  };

  const createDisplayName = (str: string) => {
    return str.replace(/_/g, " ");
  };

  const createChoiceValue = (str: string) => {
    return str.replace(/<.*?>/g, "");
  };

  const getRequiredFields = (fields: any) => {
    return fields.map((field: any) => {
      if (field.required === true) {
        return field.name;
      }
    });
  };

  return (
    <>
      <FormControl>
        <Grid container spacing={3}>
          {formData &&
            formData.map((field: any) => (
              <>
                {checkField(field) &&
                  ((field.type === "CharField" && (
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
                            multiple
                            variant="outlined"
                            onChange={handleChoice}
                            input={<OutlinedInput label={createDisplayName(field.name)} />}
                            sx={{ width: "10rem" }}
                          >
                            {field.choices &&
                              Object.values(field.choices).map((choice: any) => (
                                <MenuItem key={choice} value={choice}>
                                  {createChoiceValue(choice)}
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

export default DyanmicForm;
