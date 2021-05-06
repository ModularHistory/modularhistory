import { Container, Grid, makeStyles } from "@material-ui/core";
import { useRouter } from "next/router";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import axiosWithoutAuth from "../../axiosWithoutAuth";
import PageTransitionContext from "../PageTransitionContext";
import CheckboxGroup from "./CheckboxGroup";
import MultiSelect from "./MultiSelect";
import RadioGroup from "./RadioGroup";
import SearchButton from "./SearchButton";
import TextField from "./StyledTextField";
import YearSelect from "./YearSelect";

export const SearchFormContext = createContext({});

/**
 * This hook is used to centralize the state of all search form inputs.
 * Returns an object containing:
 *   `state`: the current values for all inputs.
 *   `setState`: function that directly sets the state.
 *   `setStateFromEvent`: function that accepts an event and extracts
 *                        the new state from the event.
 */
function useSearchFormState() {
  const router = useRouter();

  // load the initial state from url query params
  const [state, setState] = useState(router.query);

  // event handler used by several inputs to set their state
  const setStateFromEvent = useCallback(
    ({ target }) => setState((prevState) => ({ ...prevState, [target.name]: target.value })),
    []
  );

  useEffect(() => {
    // Remove any params we don't want sent to the next search page
    // and update form state when browser history is navigated.
    const { page, ...query } = router.query;
    setState(query);
  }, [router.query]);

  // Disable the entire form when page transition are occurring
  const isLoading = useContext(PageTransitionContext);

  return { state, setState, setStateFromEvent, disabled: isLoading };
}

const useStyles = makeStyles((theme) => ({
  root: {
    paddingTop: "20px",
    maxWidth: ({ inSidebar }) => (inSidebar ? undefined : theme.breakpoints.values.sm),
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
    "&:last-child": { marginBottom: "50px" },
  },
}));

/**
 * A component for an advanced/full search form.
 * `inSidebar` is a boolean determining whether the form should be
 *    forced to display vertically, as when constrained by a sidebar.
 *    If false, the inputs may be rendered side-by-side.
 */
export default function SearchForm({ inSidebar }) {
  const classes = useStyles({ inSidebar });
  const router = useRouter();
  const formState = useSearchFormState();

  // When `sm` is 6, inputs may be rendered side-by-side.
  // See: https://material-ui.com/components/grid/#grid-with-breakpoints
  const sm = inSidebar ? 12 : 6;

  return (
    <SearchFormContext.Provider value={formState}>
      <Container className={classes.root}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={sm}>
            <TextField
              label="Query"
              name="query"
              value={formState.state["query"] || ""}
              disabled={formState.disabled}
              onChange={formState.setStateFromEvent}
            />
          </Grid>

          <Grid item xs={12} sm={sm}>
            <RadioGroup label={"Ordering"} name={"ordering"}>
              {["Relevance", "Date"]}
            </RadioGroup>
          </Grid>

          <Grid container item xs={12} sm={sm}>
            <YearSelect label={"Start year"} name={"start_year"} />
          </Grid>
          <Grid container item xs={12} sm={sm}>
            <YearSelect label={"End year"} name={"end_year"} />
          </Grid>

          <Grid item xs={12} sm={sm}>
            <MultiSelect label={"Entities"} name={"entities"} keyName={"id"} valueName={"name"}>
              {() =>
                axiosWithoutAuth
                  .get("/api/entities/partial/?attributes=id&attributes=name")
                  .then((response) => response.data["results"])
                  .catch((error) => console.log(">>>", error.request))
              }
            </MultiSelect>
          </Grid>

          <Grid item xs={12} sm={sm}>
            <MultiSelect label={"Topics"} name={"topics"} keyName={"pk"} valueName={"name"}>
              {() =>
                axiosWithoutAuth
                  .get("/api/topics/partial/")
                  .then((response) => response.data["results"])
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
                { label: "Occurrences", key: "occurrences.occurrence" },
                { label: "Quotes", key: "quotes.quote" },
                { label: "Images", key: "images.image" },
                { label: "Sources", key: "sources.source" },
                { label: "Entities", key: "entities.entity" },
              ]}
            </CheckboxGroup>
          </Grid>

          <Grid item xs={12}>
            <SearchButton onClick={() => router.push({ query: formState.state })} />
          </Grid>
        </Grid>
      </Container>
    </SearchFormContext.Provider>
  );
}
