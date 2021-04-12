import {
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup as MuiRadioGroup,
} from "@material-ui/core";
import { useContext } from "react";
import { SearchFormContext } from "./SearchForm";

export default function RadioGroup({ label, name, children }) {
  // A component for radio input in the search form.
  // `label` is displayed above the radio group.
  // `name` is the query parameter key used in the search API request.
  // `children` is an array of options (strings).
  //    The value of the option to be used in API requests is
  //    assumed to be the lowercase of each option.

  const { state, setStateFromEvent, disabled } = useContext(SearchFormContext);

  // if state is not specified, default to the first option
  const value = state[name] || children[0].toLowerCase();

  // See the demo at
  // https://material-ui.com/components/radio-buttons/#radiogroup
  return (
    <FormControl component="fieldset" disabled={disabled}>
      <FormLabel component="legend">{label}</FormLabel>
      <MuiRadioGroup name={name} value={value} onChange={setStateFromEvent}>
        {children.map((opt) => (
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
}
