import TextField from "./StyledTextField";
import { Grid, MenuItem } from "@material-ui/core";
import { useContext } from "react";
import { SearchFormContext } from "./SearchForm";

/**
 * A component for year range inputs in the search form.
 * `label` is displayed in the number input.
 * `name` is the query parameter key used in the search API request.
 */
export default function YearSelect({ label, name }) {
  const { state, setStateFromEvent, disabled } = useContext(SearchFormContext);

  // `typeName` is the query param key for the year type (e.g. "CE").
  // TODO: this feature is not yet implemented.
  const typeName = `${name}_type`;

  // set default values if not in state
  const value = state[name] ?? "";
  const type = state[typeName] ?? "CE";

  // https://material-ui.com/api/text-field/
  return (
    <>
      <Grid item xs={6}>
        <TextField
          label={label}
          type={"number"}
          InputProps={{ inputProps: { min: 1 } }}
          name={name}
          value={value}
          onChange={setStateFromEvent}
          disabled={disabled}
        />
      </Grid>
      <Grid item xs={6}>
        <TextField
          select
          name={typeName}
          value={type}
          onChange={setStateFromEvent}
          disabled={true} // disabled={disabled}
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
