import { Grid, MenuItem } from "@mui/material";
import { FC } from "react";
import TextField from "../forms/StyledTextField";

interface YearSelectProps {
  label: string;
  defaultYearValue: string;
  defaultTypeValue: string;
  onYearChange: (value: string) => void;
  onTypeChange: (value: string) => void;
  disabled?: boolean;
}

/**
 * A component for year range inputs in the search form.
 * `label` is displayed in the number input.
 */
const YearSelect: FC<YearSelectProps> = ({
  label,
  defaultYearValue,
  defaultTypeValue,
  onYearChange,
  onTypeChange,
  disabled,
}: YearSelectProps) => {
  return (
    <>
      <Grid item xs={6} sm={8}>
        <TextField
          label={label}
          type={"number"}
          inputProps={{ min: 1 }}
          defaultValue={defaultYearValue}
          onChange={(e) => onYearChange(e.target.value)}
          disabled={disabled}
        />
      </Grid>
      <Grid item xs={6} sm={4}>
        <TextField
          select
          onChange={(e) => onTypeChange(e.target.value)}
          defaultValue={defaultTypeValue ?? "CE"}
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
