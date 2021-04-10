import axios from "axios";

import YearSelect from "./YearSelect";
import TextField from "./StyledTextField";
import RadioGroup from "./RadioGroup";

import {useRouter} from "next/router";
import {Container, Grid} from "@material-ui/core";
import {useState, createContext, useCallback} from "react";
import {makeStyles} from "@material-ui/styles";
import MultiSelect from "./MultiSelect";
import CheckboxGroup from "./CheckboxGroup";
import SearchButton from "./SearchButton";

export const SearchFormContext = createContext([]);

function useFormState(initialState) {
  const [state, setState] = useState(initialState);
  const setStateFromEvent = useCallback(({target}) => setState(
    (prevState) => ({...prevState, [target.name]: target.value})
  ), []);
  return [state, setStateFromEvent, setState];
}

const useStyles = makeStyles({
  root: {
    paddingTop: "20px",
    // marginRight: "12px",
    "& input": {
      backgroundColor: "white",
    },
    "& .MuiTextField-root": {
      backgroundColor: "white",
    },
    "& .MuiRadio-root, & .MuiCheckbox-root": {
      marginBottom: "-9px",
      marginTop: "-9px",
    },
    // to prevent hidden search button when navbar is visible
    "&:last-child": { marginBottom: "50px" }
  },
});

export default function SearchForm() {
  const classes = useStyles();
  const router = useRouter();

  const [state, setStateFromEvent, setState] = useFormState(router.query);

  return (
    <SearchFormContext.Provider value={[state, setStateFromEvent, setState]}>
      <Container className={classes.root}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField label="Query"
                       name="query"
                       value={state["query"]}
                       onChange={setStateFromEvent}
            />
          </Grid>

          <Grid item xs={12}>
            <RadioGroup label={"Ordering"}>
              {["Date", "Relevance"]}
            </RadioGroup>
          </Grid>

          <YearSelect label={"Start year"} name={"start_year"}/>
          <YearSelect label={"End year"} name={"end_year"}/>

          <Grid item xs={12}>
            <MultiSelect label={"Entities"}
                         name={"entities"}
                         keyName={"id"}
                         valueName={"name"}>
              {() => axios
                .get("/api/entities/partial/?attributes=id&attributes=name")
                .then(response => response.data["results"])
              }
            </MultiSelect>
          </Grid>

          <Grid item xs={12}>
            <MultiSelect label={"Topics"}
                         name={"topics"}
                         keyName={"pk"}
                         valueName={"key"}>
              {() => axios
                .get("/api/topics/partial/")
                .then(response => response.data["results"])
              }
            </MultiSelect>
          </Grid>

          <Grid item xs={12}>
            <RadioGroup label={"Quality"} disabled>
              {["All", "Verified"]}
            </RadioGroup>
          </Grid>

          <Grid item xs={12}>
            <CheckboxGroup label={"Content Types"} name={"content_types"}>
              {[
                {label: "Occurrences", key: "occurrences.occurrence"},
                {label: "Quotes", key: "quotes.quote"},
                {label: "Images", key: "images.image"},
                {label: "Sources", key: "sources.source"},
              ]}
            </CheckboxGroup>
          </Grid>

          <Grid item xs={12}>
            <SearchButton
              onClick={() => router.push({
                pathname: "/search",
                query: state
              })}
            />
          </Grid>
        </Grid>
      </Container>
    </SearchFormContext.Provider>
  );
}
