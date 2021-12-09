import axiosWithAuth from "@/axiosWithAuth";
import axiosWithoutAuth from "@/axiosWithoutAuth";
import HTMLEditor from "@/components/forms/HTMLEditor";
import { InstantSearch } from "@/components/search/InstantSearch";
import YearSelect from "@/components/search/YearSelect";
import {
  Autocomplete,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  FormControl,
  Grid,
  GridProps,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  TextFieldProps,
} from "@mui/material";
import { FC, useEffect, useRef, useState } from "react";

const DynamicForm: FC = () => {
  const [contentType, setContentType] = useState("");

  const handleContentTypeChange = (event: { target: { value: string } }) => {
    setContentType(event.target.value);
  };

  return (
    <Card raised>
      <CardContent>
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
      </CardContent>
    </Card>
  );
};

interface DynamicFormFieldsProps {
  contentType: string;
}

interface Field {
  name: string;
  type:
    | "PrimaryKeyRelatedField"
    | "ManyRelatedField"
    | "CharField"
    | "HistoricDateTimeField"
    | "JSONField"
    | "ListField"
    | "ListSerializer";
  editable: boolean;
  required: boolean;
  allowBlank: boolean | null;
  verboseName: string | null;
  helpText: string | null;
  choices: Record<string, string> | null;
  style: Record<string, any>;
  isHtml?: boolean;
  instantSearch?: {
    model: string;
    filters: Record<string, any>;
  };
  childFields?: Field[];
}

//Dynamic fields form
//Can be called using the DynamicForm component or by using the DynamicFormFields prop and specifying the 'type' prop
const DynamicFormFields: FC<DynamicFormFieldsProps> = ({ contentType }: DynamicFormFieldsProps) => {
  const [fields, setFields] = useState<{ required: Field[]; optional: Field[] }>({
    required: [],
    optional: [],
  });
  const fieldValuesRef = useRef<Record<string, any>>({});

  const getDynamicFields = (contentType: string): Promise<Field[]> =>
    axiosWithoutAuth.get(`/api/${contentType}/fields/`).then((response) => response.data);

  useEffect(() => {
    getDynamicFields(contentType).then((result) => {
      const editableFields = result.sort((a, b) => Number(a.isHtml ?? 0) - Number(b.isHtml ?? 0));
      setFields({
        required: editableFields.filter((field) => field.required),
        optional: editableFields.filter((field) => !field.required),
      });
    });
  }, [contentType]);

  return (
    <>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Divider textAlign={"left"} sx={{ mb: 2 }}>
            <strong>Required</strong>
          </Divider>
        </Grid>
        {fields.required.map((field, index) => (
          <DynamicField
            key={index}
            field={field}
            onChange={(value) => (fieldValuesRef.current[field.name] = value)}
            gridProps={{ item: true, xs: 12, sm: 6, md: 4 }}
          />
        ))}
        <Grid item xs={12}>
          <Divider textAlign={"left"} sx={{ mb: 2 }}>
            <strong>Optional</strong>
          </Divider>
        </Grid>
        {fields.optional.map((field, index) => (
          <DynamicField
            key={index}
            field={field}
            onChange={(value) => (fieldValuesRef.current[field.name] = value)}
            gridProps={{ item: true, xs: 12, sm: 6, md: 4 }}
          />
        ))}
      </Grid>
      <Button
        variant="contained"
        sx={{ m: "1rem" }}
        onClick={() => {
          console.log(fieldValuesRef.current);
          axiosWithAuth
            .post(`/api/${contentType}/`, fieldValuesRef.current)
            .then(console.log)
            .catch(console.error);
        }}
      >
        Submit
      </Button>
      <Box component={"pre"} maxWidth={"80vw"}>
        {JSON.stringify(fields, null, 4)}
      </Box>
    </>
  );
};

const DynamicField: FC<{ field: Field; gridProps: GridProps; onChange: (state: any) => void }> = ({
  field,
  onChange,
  gridProps,
}) => {
  const commonProps: Omit<TextFieldProps, "label"> & { label: string } = {
    required: field.required && !(field.type === "CharField" && field.allowBlank),
    label: createDisplayName(field.name),
    helperText: field.helpText,
    variant: "outlined",
    fullWidth: true,
    sx: { minWidth: "5rem" },
  };

  const renderedField = (() => {
    if (field.instantSearch) {
      return (
        <InstantSearch
          label={commonProps.label}
          getDataForInput={(input) =>
            axiosWithoutAuth
              .get(`/api/search/instant/`, {
                params: { model: field.instantSearch?.model, query: input },
              })
              .then(({ data }) => data)
          }
          // TODO: set labelKey based on indexed fields?
          labelKey={"name"}
          multiple={field.type === "ManyRelatedField"}
          onChange={onChange}
        />
      );
    } else if (field.isHtml) {
      gridProps = { ...gridProps, sm: undefined, md: undefined };
      return <HTMLEditor onChange={onChange} placeholder={commonProps.label} />;
    }
    switch (field.type) {
      case "CharField":
        return field.choices ? (
          <Autocomplete
            options={Object.keys(field.choices)}
            getOptionLabel={(optionKey) => field.choices?.[optionKey] ?? ""}
            onChange={(e, value) => onChange(value ? field.choices?.[value] : undefined)}
            renderInput={(params) => <TextField {...params} {...commonProps} />}
          />
        ) : (
          <TextField
            {...commonProps}
            multiline
            onChange={(e) => {
              onChange(e.target.value);
            }}
          />
        );
      case "PrimaryKeyRelatedField":
        return (
          <TextField {...commonProps} select onChange={onChange}>
            {Object.entries(field.choices ?? {}).map(([id, choice]) => (
              <MenuItem value={id} key={id}>
                <span dangerouslySetInnerHTML={{ __html: choice }} />
              </MenuItem>
            ))}
          </TextField>
        );
      case "HistoricDateTimeField":
        return <YearSelect label={commonProps.label} onChange={onChange} />;
      case "ListField":
        return (
          <Autocomplete
            multiple
            freeSolo
            options={[]}
            onChange={onChange}
            renderInput={(params) => <TextField {...params} {...commonProps} />}
          />
        );
      case "ListSerializer":
      case "ManyRelatedField":
      case "JSONField":
      default:
        console.error(`Unexpected field type encountered: ${JSON.stringify(field, null, 2)}`);
        return <TextField {...commonProps} disabled />;
    }
  })();

  return <Grid {...gridProps}>{renderedField}</Grid>;
};

function createDisplayName(str: string) {
  str = str.replace(/_/g, " ");
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function stripHTML(str: string) {
  return str.replace(/<.*?>/g, "");
}

export default DynamicForm;
