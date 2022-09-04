import {
  Checkbox,
  CheckboxProps,
  FormControl,
  FormControlLabel,
  FormGroup,
  FormLabel,
} from "@mui/material";
import { FC, useRef } from "react";

interface CheckboxGroupProps {
  label: string;
  defaultValue: string;
  onChange: (value: string[]) => void;
  options: Array<{
    key: string;
    label?: string;
    defaultChecked?: boolean;
  }>;
  disabled?: boolean;
  row?: boolean;
}

/**
 * A component for checkbox inputs in the search form.
 * `label` is displayed above the checkboxes.
 * `name` is the query parameter key used in the search API request.
 * `children` is an array of options, objects with keys `label` and `key`.
 *   `label` is rendered next to the option.
 *   `key` is the value of the option used in the API request.
 */
const CheckboxGroup: FC<CheckboxGroupProps> = ({
  label,
  onChange,
  options,
  disabled,
  row,
}: CheckboxGroupProps) => {
  // prevent a warning about defaultValue changing after initial render
  const defaultChecks = useRef(
    Object.fromEntries(options.map(({ key, defaultChecked }) => [key, defaultChecked ?? true]))
  ).current;

  const checks = useRef(defaultChecks).current;

  const handleChange: CheckboxProps["onChange"] = ({ target }, checked) => {
    checks[target.name] = checked;
    onChange(
      Object.entries(checks).reduce((checkedOptionKeys: string[], [key, checked]) => {
        if (checked) checkedOptionKeys.push(key);
        return checkedOptionKeys;
      }, [])
    );
  };

  // The component structure below is similar to the demo at
  // https://material-ui.com/components/checkboxes/#checkboxes-with-formgroup
  return (
    <FormControl
      component="fieldset"
      disabled={disabled}
      sx={{ border: "1px solid lightgray", paddingX: "0.6rem", borderRadius: "4px" }}
    >
      <FormLabel component="legend">{label}</FormLabel>
      <FormGroup row={row}>
        {options.map(({ label, key }) => (
          <FormControlLabel
            control={
              <Checkbox
                defaultChecked={defaultChecks[key]}
                onChange={handleChange}
                name={key}
                color={"primary"}
              />
            }
            label={label ?? key.charAt(0).toUpperCase() + key.substr(1)}
            key={key}
          />
        ))}
      </FormGroup>
    </FormControl>
  );
};

export default CheckboxGroup;
