import axios from "axios";

import {
  useState,
  useContext,
  createContext,
  useCallback,
  useEffect
} from "react";
import {useRouter} from "next/router";
import {Container, Grid} from "@material-ui/core";
import {makeStyles} from "@material-ui/core";

import MultiSelect from "./MultiSelect";
import CheckboxGroup from "./CheckboxGroup";
import SearchButton from "./SearchButton";
import YearSelect from "./YearSelect";
import TextField from "./StyledTextField";
import RadioGroup from "./RadioGroup";

import PageTransitionContext from "../PageTransitionContext";

export const SearchFormContext = createContext({});

function useSearchFormState() {
  const router = useRouter();
  const [state, setState] = useState(router.query);
  const setStateFromEvent = useCallback(({target}) => setState(
    (prevState) => ({...prevState, [target.name]: target.value})
  ), []);

  useEffect(() => {
    // Remove any params we don't want sent to the next search page
    // and update form state when browser history is navigated.
    const {page, ...query} = router.query;
    setState(query);
  }, [router.query]);

  const isLoading = useContext(PageTransitionContext);

  return {state, setState, setStateFromEvent, disabled: isLoading};
}

const useStyles = makeStyles((theme) => ({
  root: {
    paddingTop: "20px",
    maxWidth: ({contained}) => contained ? undefined : theme.breakpoints.values.sm,
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
    "&:last-child": {marginBottom: "50px"}
  },
}));

export default function SearchForm({contained}) {
  const classes = useStyles({contained});
  const router = useRouter();
  const formState = useSearchFormState();

  const sm = contained ? 12 : 6;

  return (
    <SearchFormContext.Provider value={formState}>
      <Container className={classes.root}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={sm}>
            <TextField label="Query"
                       name="query"
                       value={formState.state["query"] || ""}
                       disabled={formState.disabled}
                       onChange={formState.setStateFromEvent}
            />
          </Grid>

          <Grid item xs={12} sm={sm}>
            <RadioGroup label={"Ordering"} name={"ordering"}>
              {["Date", "Relevance"]}
            </RadioGroup>
          </Grid>

          <Grid container item xs={12} sm={sm}>
            <YearSelect label={"Start year"} name={"start_year"}/>
          </Grid>
          <Grid container item xs={12} sm={sm}>
            <YearSelect label={"End year"} name={"end_year"}/>
          </Grid>

          <Grid item xs={12} sm={sm}>
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

          <Grid item xs={12} sm={sm}>
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

          <Grid item xs={12} sm={sm}>
            <RadioGroup label={"Quality"} name={"quality"}>
              {["All", "Verified"]}
            </RadioGroup>
          </Grid>

          <Grid item xs={12} sm={sm}>
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
              onClick={
                () => router.push({pathname: "/search", query: formState.state})
              }
            />
          </Grid>
        </Grid>
      </Container>
    </SearchFormContext.Provider>
  );
}
