import TextField from "./StyledTextField";
import { Grid, MenuItem } from "@material-ui/core";
import { useContext } from "react";
import { SearchFormContext } from "./SearchForm";

export default function YearSelect({ label, name }) {
  // A component for year range inputs in the search form.
  // `label` is displayed in the number input.
  // `name` is the query parameter key used in the search API request.

  const { state, setStateFromEvent, disabled } = useContext(SearchFormContext);

  // `valueName` is the query param key for the year value (number).
  // `typeName` is the query param key for the value type (e.g. "CE").
  // These formats were chosen only because the API already supports them.
  const valueName = `${name}_0`;
  const typeName = `${name}_1`;

  // set default values if not in state
  const yearValue = state[valueName] ?? "";
  const yearType = state[typeName] ?? "CE";

  // https://material-ui.com/api/text-field/
  return (
    <>
      <Grid item xs={6}>
        <TextField
          label={label}
          type={"number"}
          InputProps={{ inputProps: { min: 1 } }}
          name={valueName}
          value={yearValue}
          onChange={setStateFromEvent}
          disabled={disabled}
        />
      </Grid>
      <Grid item xs={6}>
        <TextField
          select
          name={typeName}
          value={yearType}
          onChange={setStateFromEvent}
          disabled={disabled}
        >
          {["CE", "BCE", "YBP"].map((opt) => (
            <MenuItem value={opt} key={opt}>
              {opt}
            </MenuItem>
          ))}
        </TextField>
      </Grid>
    </>
  );
}
