import {
  Checkbox,
  CheckboxProps,
  FormControl,
  FormControlLabel,
  FormGroup,
  FormLabel,
} from "@mui/material";
import { FC, useRef, useState } from "react";

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
  defaultValue,
  onChange,
  options,
  disabled,
}: CheckboxGroupProps) => {
  // If the current state is not set, default to all options.
  // This is the default behavior expected by the API.

  const optionStates = useRef(
    Object.fromEntries(options.map(({ key, defaultChecked }) => [key, defaultChecked ?? true]))
  );

  // event handler for user input
  const handleChange: CheckboxProps["onChange"] = ({ target }, checked) => {
    optionStates.current[target.name] = checked;
    onChange(
      Object.entries(optionStates.current).reduce((checkedOptionKeys: string[], [key, checked]) => {
        if (checked) checkedOptionKeys.push(key);
        return checkedOptionKeys;
      }, [])
    );
  };

  // The component structure below is similar to the demo at
  // https://material-ui.com/components/checkboxes/#checkboxes-with-formgroup
  return (
    <FormControl component="fieldset" disabled={disabled}>
      <FormLabel component="legend">{label}</FormLabel>
      <FormGroup>
        {options.map(({ label, key }) => (
          <FormControlLabel
            control={
              <Checkbox
                defaultChecked={
                  // prevent a warning about defaultValue changing after initial render
                  useState(() => defaultValue?.includes(key) ?? optionStates.current[key])[0]
                }
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
