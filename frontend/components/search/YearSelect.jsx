import TextField from "./StyledTextField";
import {Grid, MenuItem} from "@material-ui/core";

export default function YearSelect({label, name, state, setState}) {
  const valueName = `${name}_0`;
  const typeName = `${name}_1`;

  const yearValue = state[valueName] ?? 0;
  const yearType = state[typeName] ?? "CE";

  return (
    <Grid container item xs={12}>
      <Grid item xs={6}>
        <TextField label={label}
               type={"number"}
               name={valueName}
               value={yearValue}
               onChange={setState}/>
      </Grid>
      <Grid item xs={6}>
        <TextField select name={typeName} value={yearType} onChange={setState}>
          {["CE", "BCE", "YBP"].map((opt) => (
            <MenuItem value={opt} key={opt}>{opt}</MenuItem>
          ))}
        </TextField>
      </Grid>
    </Grid>
  );
}