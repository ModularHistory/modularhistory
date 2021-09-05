import {
  Checkbox,
  CheckboxProps,
  FormControl,
  FormControlLabel,
  FormGroup,
  FormLabel,
} from "@material-ui/core";
import { FC, useContext } from "react";
import { SearchFormContext } from "./SearchForm";

interface CheckboxGroupProps {
  label: string;
  name: string;
  children: Array<{
    label: string;
    key: string;
    defaultChecked?: boolean;
  }>;
}

/**
 * A component for checkbox inputs in the search form.
 * `label` is displayed above the checkboxes.
 * `name` is the query parameter key used in the search API request.
 * `children` is an array of options, objects with keys `label` and `key`.
 *   `label` is rendered next to the option.
 *   `key` is the value of the option used in the API request.
 */
const CheckboxGroup: FC<CheckboxGroupProps> = ({ label, name, children }: CheckboxGroupProps) => {
  // get current input values
  const { formState, setFormState, disabled } = useContext(SearchFormContext);

  // If the current state is not set, default to all options.
  // This is the default behavior expected by the API.
  const state = formState[name];
  let checkedItems: string[];
  if (state) {
    checkedItems = (Array.isArray(state) ? state : [state]).map(String);
  } else {
    checkedItems = children.reduce((filtered: string[], item) => {
      if (item.defaultChecked !== false) filtered.push(item.key);
      return filtered;
    }, []);
  }

  // event handler for user input
  const handleChange: CheckboxProps["onChange"] = ({ target }, checked) => {
    if (checked) {
      // add option to selected values
      checkedItems.push(target.name);
    } else {
      // remove option from selected values
      const index = checkedItems.findIndex((item) => item === target.name);
      if (index >= 0) checkedItems.splice(index, 1);
    }
    setFormState((prevState) => ({ ...prevState, [name]: checkedItems }));
  };

  // The component structure below is similar to the demo at
  // https://material-ui.com/components/checkboxes/#checkboxes-with-formgroup
  return (
    <FormControl component="fieldset" disabled={disabled}>
      <FormLabel component="legend">{label}</FormLabel>
      <FormGroup>
        {children.map(({ label, key }) => (
          <FormControlLabel
            control={
              <Checkbox
                checked={checkedItems.includes(key)}
                onChange={handleChange}
                name={key}
                color={"primary"}
              />
            }
            label={label}
            key={key}
          />
        ))}
      </FormGroup>
    </FormControl>
  );
};

export default CheckboxGroup;
