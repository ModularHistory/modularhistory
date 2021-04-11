import {
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
  FormLabel
} from "@material-ui/core";
import {useContext} from "react";
import {SearchFormContext} from "./SearchForm";

export default function CheckboxGroup({label, name, children}) {
  // A component for checkbox inputs in the search form.
  // `label` is displayed above the checkboxes.
  // `name` is the query parameter key used in the search API request.
  // `children` is an array of options, objects with keys `label` and `key`.
  //    `label` is rendered next to the option.
  //    `key` is the value of the option used in the API request.

  // get current input values
  const {state, setState, disabled} = useContext(SearchFormContext);

  // If the current state is not set, default to all options.
  // This is the default behavior expected by the API.
  let checkedItems = state[name] || children.map(({key}) => key);

  // event handler for user input
  const handleChange = ({target}) => {
    if (target.checked) {
      // add option to selected values
      checkedItems.push(target.name);
    } else {
      // remove option from selected values
      const index = checkedItems.findIndex((item) => item === target.name);
      if (index >= 0) checkedItems.splice(index, 1);
    }
    setState((prevState) => ({...prevState, [name]: checkedItems}));
  };

  // The component structure below is similar to the demo at
  // https://material-ui.com/components/checkboxes/#checkboxes-with-formgroup
  return (
    <FormControl component="fieldset" disabled={disabled}>
      <FormLabel component="legend">{label}</FormLabel>
      <FormGroup>
        {children.map(({label, key}) => (
          <FormControlLabel
            control={
              <Checkbox checked={checkedItems.includes(key)}
                        onChange={handleChange}
                        name={key}
                        color={"primary"}/>
            }
            label={label}
            key={key}
          />
        ))}
      </FormGroup>
    </FormControl>
  );
}