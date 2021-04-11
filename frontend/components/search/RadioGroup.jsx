import {
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup as MuiRadioGroup
} from "@material-ui/core";
import {useContext} from "react";
import {SearchFormContext} from "./SearchForm";

export default function RadioGroup({label, name, children}) {
  const {state, setStateFromEvent, disabled} = useContext(SearchFormContext);

  const value = state[name] || children[0].toLowerCase();

  return (
    <FormControl component="fieldset" disabled={disabled}>
      <FormLabel component="legend">{label}</FormLabel>
      <MuiRadioGroup name={name} value={value} onChange={setStateFromEvent}>
        {children.map((opt) => (
          <FormControlLabel label={opt}
                            key={opt}
                            value={opt.toLowerCase()}
                            control={<Radio color={"primary"}/>}
          />
        ))}
      </MuiRadioGroup>
    </FormControl>
  );
}
