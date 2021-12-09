import TextField from "@/components/forms/StyledTextField";
import { EntitiesInstantSearch, TopicsInstantSearch } from "@/components/search/InstantSearch";
import { Container, Grid } from "@mui/material";
import { styled } from "@mui/material/styles";
import { useRouter } from "next/router";
import type { ParsedUrlQueryInput } from "querystring";
import { FC, KeyboardEventHandler, MutableRefObject, useContext, useRef } from "react";
import PageTransitionContext from "../PageTransitionContext";
import CheckboxGroup from "./CheckboxGroup";
import RadioGroup from "./RadioGroup";
import SearchButton from "./SearchButton";
import YearSelect from "./YearSelect";

const fields = [
  "query",
  "ordering",
  "startYear",
  "startYearType",
  "endYear",
  "endYearType",
  "entities",
  "topics",
  "quality",
  "contentTypes",
] as const;
type Field = typeof fields[number];
type FieldsRef = MutableRefObject<Record<Field, any>>;
type FieldCallbacks = Record<Field, (value: ParsedUrlQueryInput[string]) => void>;

export interface SearchFormProps {
  inSidebar?: boolean;
}

const StyledContainer = styled(Container)({
  paddingTop: "20px",
  // maxWidth: ({ inSidebar }) => (inSidebar ? undefined : theme.breakpoints.values.sm),
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
});

/**
 * A component for an advanced/full search form.
 * `inSidebar` is a boolean determining whether the form should be
 *    forced to display vertically, as when constrained by a sidebar.
 *    If false, the inputs may be rendered side-by-side.
 */
const SearchForm: FC<SearchFormProps> = ({ inSidebar = false }: SearchFormProps) => {
  const router = useRouter();
  const isLoading = useContext(PageTransitionContext);

  const fieldsRef = useRef(
    Object.fromEntries(fields.map((name) => [name, router.query[name]]))
  ) as FieldsRef;
  const fieldCallbacks = Object.fromEntries(
    fields.map((name) => [name, (value: any) => (fieldsRef.current[name] = value)])
  ) as FieldCallbacks;

  // When `sm` is 6, inputs may be rendered side-by-side.
  // See: https://material-ui.com/components/grid/#grid-with-breakpoints
  const sm = inSidebar ? 12 : 6;

  const submitForm = () => {
    const queryParams = { ...fieldsRef.current };
    for (const name in queryParams) {
      if (!queryParams[name as Field]) delete queryParams[name as Field];
    }

    router.push({
      query: queryParams,
    });
  };

  const handleKeyUp: KeyboardEventHandler = (event) => {
    if (event.key === "Enter") {
      submitForm();
    }
  };

  return (
    <StyledContainer data-testid={"searchForm"}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={sm}>
          <TextField
            label="Query"
            defaultValue={fieldsRef.current.query}
            onChange={(e) => fieldCallbacks.query(e.target.value)}
            onKeyUp={handleKeyUp}
            disabled={isLoading}
            data-testid={"queryField"}
          />
        </Grid>

        <Grid item xs={12} sm={sm}>
          <RadioGroup
            label={"Ordering"}
            defaultValue={fieldsRef.current.ordering}
            onChange={fieldCallbacks.ordering}
            options={["Relevance", "Date"]}
            disabled={isLoading}
          />
        </Grid>

        <Grid container item xs={12} sm={sm}>
          <YearSelect
            label={"Start year"}
            defaultYearValue={fieldsRef.current.startYear}
            defaultTypeValue={fieldsRef.current.startYearType}
            onYearChange={fieldCallbacks.startYear}
            onTypeChange={fieldCallbacks.startYearType}
            disabled={isLoading}
          />
        </Grid>
        <Grid container item xs={12} sm={sm}>
          <YearSelect
            label={"End year"}
            defaultYearValue={fieldsRef.current.endYear}
            defaultTypeValue={fieldsRef.current.endYearType}
            onYearChange={fieldCallbacks.endYear}
            onTypeChange={fieldCallbacks.endYearType}
            disabled={isLoading}
          />
        </Grid>

        <Grid item xs={12} sm={sm}>
          <EntitiesInstantSearch
            onChange={fieldCallbacks.entities}
            disabled={isLoading}
            defaultValue={fieldsRef.current.entities}
          />
        </Grid>

        <Grid item xs={12} sm={sm}>
          <TopicsInstantSearch
            onChange={fieldCallbacks.topics}
            disabled={isLoading}
            defaultValue={fieldsRef.current.topics}
          />
        </Grid>

        <Grid item xs={12} sm={sm}>
          <RadioGroup
            label={"Quality"}
            defaultValue={fieldsRef.current.quality}
            onChange={fieldCallbacks.quality}
            options={["All", "Verified"]}
            disabled={isLoading}
          />
        </Grid>

        <Grid item xs={12} sm={sm}>
          {/* #ContentTypesHardCoded */}
          <CheckboxGroup
            label={"Content Types"}
            defaultValue={fieldsRef.current.contentTypes}
            onChange={fieldCallbacks.contentTypes}
            disabled={isLoading}
            options={[
              { key: "occurrences" },
              { key: "quotes" },
              { key: "images", defaultChecked: false },
              { key: "sources" },
              { key: "entities" },
            ].map(({ key, defaultChecked }) => ({
              key,
              defaultChecked:
                fieldsRef.current.contentTypes?.includes(key) ?? defaultChecked ?? true,
            }))}
          />
        </Grid>

        <Grid item container xs={12} justifyContent="center" paddingY="1rem">
          <SearchButton onClick={submitForm} />
        </Grid>
      </Grid>
    </StyledContainer>
  );
};

export default SearchForm;
