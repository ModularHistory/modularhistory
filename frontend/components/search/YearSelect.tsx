import { Grid, MenuItem } from "@material-ui/core";
import { FC, useContext } from "react";
import { SearchFormContext } from "./SearchForm";
import TextField from "../forms/StyledTextField";

interface YearSelectProps {
  label: string;
  name: string;
}

const YearSelect: FC<YearSelectProps> = ({ label, name }: YearSelectProps) => {
  /**
   * A component for year range inputs in the search form.
   * `label` is displayed in the number input.
   * `name` is the query parameter key used in the search API request.
   */

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
};

export default YearSelect;
