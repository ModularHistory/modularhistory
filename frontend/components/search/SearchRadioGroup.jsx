import {
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup
} from "@material-ui/core";

export default function SearchRadioGroup({label, state, setState, children}) {
  const name = label.toLowerCase();
  const value = state[name] || children[0].toLowerCase();

  return (
    <FormControl component="fieldset">
      <FormLabel component="legend">{label}</FormLabel>
      <RadioGroup name={name} value={value} onChange={setState}>
        {children.map((opt) => (
          <FormControlLabel label={opt}
                            value={opt.toLowerCase()}
                            control={<Radio color={"primary"}/>}
          />
        ))}
      </RadioGroup>
    </FormControl>
  );
}