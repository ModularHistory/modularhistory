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
  const [state, _, setState] = useContext(SearchFormContext);
  let checkedItems = state[name] || children.map(({key}) => key);

  const handleChange = ({target}) => {
    if (target.checked) {
      checkedItems.push(target.name);
      checkedItems = [...new Set(checkedItems)];
    } else {
      const index = checkedItems.findIndex((item) => item === target.name);
      if (index >= 0) checkedItems.splice(index, 1);
    }
    setState((prevState) => ({...prevState, [name]: checkedItems}));
  };

  return (
    <FormControl component="fieldset">
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