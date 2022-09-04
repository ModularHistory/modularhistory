import {
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup as MuiRadioGroup,
} from "@mui/material";
import { FC, useState } from "react";

interface RadioGroupProps {
  label: string;
  defaultValue: string;
  onChange: (value: string) => void;
  options: string[];
  disabled?: boolean;
  row?: boolean;
}

const RadioGroup: FC<RadioGroupProps> = ({
  label,
  defaultValue,
  onChange,
  options,
  disabled,
  row,
}: RadioGroupProps) => {
  // A component for radio input in the search form.
  // `label` is displayed above the radio group.
  // `name` is the query parameter key used in the search API request.
  // `options` is an array of strings.
  //    The value of the option to be used in API requests is
  //    assumed to be the lowercase of each option.

  // See the demo at
  // https://material-ui.com/components/radio-buttons/#radiogroup
  return (
    <FormControl
      component="fieldset"
      disabled={disabled}
      sx={{ border: "1px solid lightgray", paddingX: "0.6rem", borderRadius: "4px" }}
    >
      <FormLabel component="legend">{label}</FormLabel>
      <MuiRadioGroup
        // useState prevents a warning about defaultValue changing after initial render
        defaultValue={useState(() => defaultValue ?? options[0].toLowerCase())[0]}
        onChange={(e) => onChange(e.target.value)}
        row={row}
      >
        {options.map((opt) => (
          <FormControlLabel
            label={opt}
            key={opt}
            value={opt.toLowerCase()}
            control={<Radio color={"primary"} />}
          />
        ))}
      </MuiRadioGroup>
    </FormControl>
  );
};

export default RadioGroup;
