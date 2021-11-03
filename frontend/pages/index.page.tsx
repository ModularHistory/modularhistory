import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import SearchButton from "@/components/search/SearchButton";
import {
  Box,
  Button,
  Container,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  Link,
  MenuItem,
  OutlinedInput,
  Select,
} from "@mui/material";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useRouter } from "next/router";
import { FC, MouseEventHandler, useEffect, useRef, useState } from "react";

export default function Home() {
  const router = useRouter();
  const queryInputRef = useRef<HTMLInputElement>(null);

  // event handler for pressing enter or clicking search button
  const search = ({ key }: { key?: string }) => {
    if (key && key !== "Enter") return;
    router.push({
      pathname: "/search/",
      query: { query: queryInputRef.current?.value },
    });
  };

  const searchForm = (
    <Grid
      container
      direction={"column"}
      spacing={2}
      alignItems={"center"}
      justifyContent={"center"}
    >
      <Grid item>
        <TextField
          inputRef={queryInputRef}
          id={"id_query"}
          name={"query"}
          variant={"outlined"}
          size={"small"}
          style={{ minWidth: "280px" }}
          onKeyPress={search}
          inputProps={{ "data-testid": "query" }}
        />
      </Grid>
      <Grid item>
        <SearchButton onClick={search as MouseEventHandler} data-testid={"searchButton"} />
      </Grid>
    </Grid>
  );

  return (
    <Layout>
      <Grid container spacing={2} columns={16} alignItems={"center"} justifyContent={"center"}>
        <Grid item xs={8} alignItems="center" justifyContent="center">
          <Container>
            <AboutModularHistory />
          </Container>
        </Grid>
        <Grid item xs={8}>
          <Container>
            <Box
              sx={{
                flex: "1 1",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "1.5rem 1rem 1.5rem 1rem",
              }}
            >
              <Card elevation={5}>
                <CardContent>
                  <Container>
                    <p>Search modules by topic, entity, or keywords.</p>
                    {searchForm}
                  </Container>
                </CardContent>
              </Card>
            </Box>
            <DyanmicForm />
          </Container>
        </Grid>
      </Grid>
    </Layout>
  );
}

const AboutModularHistory: FC = () => {
  return (
    <Box
      sx={{
        flex: "1 1",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        margin: "1.5rem 1rem 1.5rem 1rem",
        p: 4,
      }}
    >
      <Card elevation={5}>
        <Box sx={{ m: 3 }}>
          <Grid container alignItems="center" justifyContent="center">
            <Grid item>
              <Typography variant="h6" gutterBottom component="div" fontWeight="bold">
                About ModularHistory
              </Typography>
            </Grid>
          </Grid>
          <p>
            ModularHistory is a nonprofit organization dedicated to helping people learn about and
            understand the history of our world, our society, and issues of modern sociopolitical
            discourse.
          </p>
          <Button variant="contained" href="/about/">
            Learn More
          </Button>
        </Box>
        <Divider variant="middle" />
        <Box sx={{ m: 3 }}>
          <Grid container alignItems="center">
            <Grid item>
              <p>
                To support ModularHistory’s mission, you can{" "}
                <Link href="/about/contributing" variant="body2">
                  {"contribute content"}
                </Link>{" "}
                and/or{" "}
                <Link href="/donations" variant="body2">
                  {" donate."}
                </Link>
              </p>
            </Grid>
          </Grid>
        </Box>
      </Card>
    </Box>
  );
};

const DyanmicForm: FC = () => {
  const [type, setType] = useState("");

  const handleFormType = (event: { target: { value: string } }) => {
    setType(event.target.value);
  };

  return (
    <>
      <Card sx={{ display: "flex" }}>
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
      </Card>
      <Box
        sx={{
          flex: "1 1",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          margin: "1.5rem 1rem 1.5rem 1rem",
        }}
      >
        {type && type != "none" && (
          <Card elevation={5} sx={{ p: "1.5rem" }}>
            <DyanmicFormFields type={type} />
          </Card>
        )}
      </Box>
    </>
  );
};

interface DyanmicFormProps {
  type: string;
}

//Dynamic fields:
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

  /*useEffect(() => {
    getDyanmicFields(choice).then((result) => {
      setChoiceValue(result);
    });
  });*/

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
        <Button variant="contained" sx={{ m: "1rem" }}>
          Submit
        </Button>
      </FormControl>
    </>
  );
};
