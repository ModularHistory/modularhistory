import {
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup as MuiRadioGroup
} from "@material-ui/core";
import {useContext} from "react";
import {SearchFormContext} from "./SearchForm";

export default function RadioGroup({label, children, disabled}) {
  const [state, setState] = useContext(SearchFormContext);
  const name = label.toLowerCase();
  const value = state[name] || children[0].toLowerCase();

  return (
    <FormControl component="fieldset">
      <FormLabel component="legend">{label}</FormLabel>
      <MuiRadioGroup name={name} value={value} onChange={setState}>
        {children.map((opt) => (
          <FormControlLabel label={opt}
                            key={opt}
                            value={opt.toLowerCase()}
                            control={<Radio color={"primary"} disabled={disabled}/>}
          />
        ))}
      </MuiRadioGroup>
    </FormControl>
  );
}
