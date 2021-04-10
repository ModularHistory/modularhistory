import TextField from "./StyledTextField";
import {Grid, MenuItem} from "@material-ui/core";
import {useContext} from "react";
import {SearchFormContext} from "./SearchForm";

export default function YearSelect({label, name}) {
  const {state, setStateFromEvent, disabled} = useContext(SearchFormContext);

  const valueName = `${name}_0`;
  const typeName = `${name}_1`;

  const yearValue = state[valueName] ?? "";
  const yearType = state[typeName] ?? "CE";

  return (
    <>
      <Grid item xs={6}>
        <TextField label={label}
                   type={"number"}
                   name={valueName}
                   value={yearValue}
                   onChange={setStateFromEvent}
                   disabled={disabled}/>
      </Grid>
      <Grid item xs={6}>
        <TextField select
                   name={typeName}
                   value={yearType}
                   onChange={setStateFromEvent}
                   disabled={disabled}>
          {["CE", "BCE", "YBP"].map((opt) => (
            <MenuItem value={opt} key={opt}>{opt}</MenuItem>
          ))}
        </TextField>
      </Grid>
    </>
  );
}