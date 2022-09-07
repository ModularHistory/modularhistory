import TextField from "@/components/forms/StyledTextField";
import { EntitiesInstantSearch, TopicsInstantSearch } from "@/components/search/InstantSearch";
import { Grid } from "@mui/material";
import { styled } from "@mui/material/styles";
import { useRouter } from "next/router";
import type { ParsedUrlQueryInput } from "querystring";
import { FC, KeyboardEventHandler, MutableRefObject, useContext, useRef } from "react";
import PageTransitionContext from "../PageTransitionContext";
import CheckboxGroup from "./CheckboxGroup";
import RadioGroup from "./RadioGroup";
import SearchButton from "./SearchButton";
import YearSelect from "./YearSelect";

interface Fields {
  query: string;
  ordering: string;
  startYear: string;
  startYearType: string;
  endYear: string;
  endYearType: string;
  entities: string[];
  topics: string[];
  quality: string;
  contentTypes: string[];
}

const fields: (keyof Fields)[] = [
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
];
type Field = typeof fields[number];
type FieldsRef = MutableRefObject<Fields>;
type FieldCallbacks = Record<Field, (value: ParsedUrlQueryInput[string]) => void>;

export interface SearchFormProps {
  inSidebar?: boolean;
}

const StyledContainer = styled("div")({
  padding: "1rem",
  display: "flex",
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
  // "&:last-child": { marginBottom: "50px" },
});

/**
 * A component for an advanced/full search form.
 * `inSidebar` is a boolean determining whether the form should be
 *    forced to display vertically, as when constrained by a sidebar.
 *    If false, the inputs may be rendered side-by-side.
 */
const SearchForm: FC<SearchFormProps> = () => {
  const router = useRouter();
  const isLoading = useContext(PageTransitionContext);

  const fieldsRef = useRef(Object.fromEntries(fields.map((name) => [name, router.query[name]])));
  const fieldCallbacks = Object.fromEntries(
    fields.map((name) => [name, (value: Fields[keyof Fields]) => (fieldsRef.current[name] = value)])
  );

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
      <Grid container spacing={3} alignItems="center">
        <Grid item xs={12} sm={6} lg={4}>
          <TextField
            label="Query"
            defaultValue={fieldsRef.current.query}
            onChange={(e) => fieldCallbacks.query(e.target.value)}
            onKeyUp={handleKeyUp}
            disabled={isLoading}
            data-testid={"queryField"}
          />
        </Grid>

        <Grid item xs={12} sm={"auto"}>
          <RadioGroup
            label={"Ordering"}
            defaultValue={fieldsRef.current.ordering as string}
            onChange={fieldCallbacks.ordering}
            options={["Relevance", "Date"]}
            disabled={isLoading}
            row
          />
        </Grid>

        <Grid container item xs={12} sm={"auto"}>
          <YearSelect
            label={"Start year"}
            defaultYearValue={fieldsRef.current.startYear as string}
            defaultTypeValue={fieldsRef.current.startYearType as string}
            onYearChange={fieldCallbacks.startYear}
            onTypeChange={fieldCallbacks.startYearType}
            disabled={isLoading}
          />
        </Grid>

        <Grid container item xs={12} sm={"auto"}>
          <YearSelect
            label={"End year"}
            defaultYearValue={fieldsRef.current.endYear as string}
            defaultTypeValue={fieldsRef.current.endYearType as string}
            onYearChange={fieldCallbacks.endYear}
            onTypeChange={fieldCallbacks.endYearType}
            disabled={isLoading}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
          <EntitiesInstantSearch
            onChange={fieldCallbacks.entities}
            disabled={isLoading}
            defaultValue={fieldsRef.current.entities ?? []}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
          <TopicsInstantSearch
            onChange={fieldCallbacks.topics}
            disabled={isLoading}
            defaultValue={fieldsRef.current.topics ?? []}
          />
        </Grid>

        <Grid item xs={12} sm={"auto"}>
          <RadioGroup
            label={"Quality"}
            defaultValue={fieldsRef.current.quality as string}
            onChange={fieldCallbacks.quality}
            options={["All", "Verified"]}
            disabled={isLoading}
            row
          />
        </Grid>

        <Grid item xs={12} sm={"auto"}>
          {/* #ContentTypesHardCoded */}
          <CheckboxGroup
            label={"Content Types"}
            defaultValue={fieldsRef.current.contentTypes as string}
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
            row
          />
        </Grid>

        <Grid item container xs={12} md={"auto"} mx={2}>
          <SearchButton onClick={submitForm} />
        </Grid>
      </Grid>
    </StyledContainer>
  );
};

export default SearchForm;
