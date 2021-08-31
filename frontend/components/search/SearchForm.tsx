import axiosWithoutAuth from "@/axiosWithoutAuth";
import TextField from "@/components/forms/StyledTextField";
import InstantSearch from "@/components/search/InstantSearch";
import { Container, Grid, Theme } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { useRouter } from "next/router";
import {
  ChangeEventHandler,
  createContext,
  Dispatch,
  FC,
  KeyboardEventHandler,
  SetStateAction,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import PageTransitionContext from "../PageTransitionContext";
import CheckboxGroup from "./CheckboxGroup";
import MultiSelect from "./MultiSelect";
import RadioGroup from "./RadioGroup";
import SearchButton from "./SearchButton";
import YearSelect from "./YearSelect";

interface SearchFormState {
  formState: Record<string, string | number | (string | number)[] | undefined>;
  setFormState: Dispatch<SetStateAction<SearchFormState["formState"]>>;
  setFormStateFromEvent: ChangeEventHandler;
  disabled: boolean;
}

export const SearchFormContext = createContext<SearchFormState>({} as SearchFormState);

/**
 * This hook is used to centralize the state of all search form inputs.
 * Returns an object containing:
 *   `state`: the current values for all inputs.
 *   `setState`: function that directly sets the state.
 *   `setStateFromEvent`: function that accepts an event and extracts
 *                        the new state from the event.
 */
function useSearchFormState(): SearchFormState {
  const router = useRouter();

  // load the initial state from url query params
  const [formState, setFormState] = useState<SearchFormState["formState"]>(router.query);

  // event handler used by several inputs to set their state
  const setFormStateFromEvent = useCallback(
    ({ target }) => setFormState((prevState) => ({ ...prevState, [target.name]: target.value })),
    []
  );

  useEffect(() => {
    // Remove any params we don't want sent to the next search page
    // and update form state when browser history is navigated.
    // eslint-disable-next-line no-unused-vars,@typescript-eslint/no-unused-vars
    const { page, ...query } = router.query;
    setFormState(query || {});
  }, [router.query]);

  // Disable the entire form when page transition are occurring
  const isLoading = useContext(PageTransitionContext);

  return { formState, setFormState, setFormStateFromEvent, disabled: isLoading };
}

interface SearchFormProps {
  inSidebar?: boolean;
}

const useStyles = makeStyles<Theme, SearchFormProps>((theme) => ({
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
const SearchForm: FC<SearchFormProps> = ({ inSidebar = false }: SearchFormProps) => {
  const classes = useStyles({ inSidebar });
  const router = useRouter();
  const formContext = useSearchFormState();

  // When `sm` is 6, inputs may be rendered side-by-side.
  // See: https://material-ui.com/components/grid/#grid-with-breakpoints
  const sm = inSidebar ? 12 : 6;

  const submitForm = () => router.push({ query: formContext.formState as any });
  const handleKeyUp: KeyboardEventHandler = (event) => {
    if (event.key === "Enter") {
      submitForm();
    }
  };

  return (
    <SearchFormContext.Provider value={formContext}>
      <Container className={classes.root}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={sm}>
            <TextField
              label="Query"
              name="query"
              defaultValue={formContext.formState["query"] || ""}
              disabled={formContext.disabled}
              onChange={formContext.setFormStateFromEvent}
              onKeyUp={handleKeyUp}
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
            <InstantSearch
              label={"Entities"}
              name={"entities"}
              labelKey={"name"}
              getDataForInput={(input, config) =>
                axiosWithoutAuth
                  .get("/api/entities/instant_search/", {
                    params: { query: input },
                    ...config,
                  })
                  .then(({ data }) => data)
              }
              getInitialValue={(ids) =>
                axiosWithoutAuth
                  .get("/graphql/", {
                    params: { query: `{ entities(ids: [${ids}]) { id name } }` },
                  })
                  .then(({ data: { data } }) => data.entities)
              }
            />
          </Grid>

          <Grid item xs={12} sm={sm}>
            <MultiSelect label={"Topics"} name={"topics"} keyName={"id"} valueName={"name"}>
              {() =>
                axiosWithoutAuth
                  .get("/graphql/", {
                    params: { query: "{ topics { id name } }" },
                  })
                  .then((response) => response.data["data"]["topics"])
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
              {{ label: "Occurrences", key: "occurrences" }}
              {{ label: "Quotes", key: "quotes" }}
              {{ label: "Images", key: "images", defaultChecked: false }}
              {{ label: "Sources", key: "sources" }}
              {{ label: "Entities", key: "entities" }}
            </CheckboxGroup>
          </Grid>

          <Grid item xs={12}>
            <SearchButton onClick={submitForm} />
          </Grid>
        </Grid>
      </Container>
    </SearchFormContext.Provider>
  );
};

export default SearchForm;
