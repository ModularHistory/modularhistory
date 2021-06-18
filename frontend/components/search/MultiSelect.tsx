import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import Autocomplete from "@material-ui/lab/Autocomplete";
import React, { FC, useContext, useEffect, useState } from "react";
import { SearchFormContext } from "./SearchForm";

const useStyles = makeStyles({
  root: {
    "& .MuiChip-root": {
      margin: 1,
      fontSize: "11px",
      height: "20px",
      "& .MuiChip-label": {
        paddingLeft: "6px",
        paddingRight: "8px",
      },
      "& .MuiChip-deleteIcon": {
        height: "18px",
        width: "18px",
        marginRight: "2px",
      },
    },
  },
});

interface MultiSelectProps {
  label: string;
  name: string;
  keyName: string;
  valueName: string;
  children: () => Promise<
    Array<{
      label: string;
      key: string;
      defaultChecked?: boolean;
    }>
  >;
}

const MultiSelect: FC<MultiSelectProps> = ({
  label,
  name,
  keyName,
  valueName,
  children,
}: MultiSelectProps) => {
  // A component for selecting multiple options from a list.
  // `Label` is the placeholder text initially rendered in the input field.
  // `name` is the query parameter key used in API requests.
  // `keyName` is the name of the attribute that uniquely identifies
  //    each option, (e.g. "pk" or "id").
  // `valueName` is the name of the attribute that should be rendered in the input.
  // `children` is a promise that returns a list of options (objects) with
  //    two attributes each, corresponding to `keyName` and `valueName`
  //
  //  Example of valid props:
  //     children = Promise.resolve([{id: 1, name: "John Smith"}, ...etc])
  //     keyName = "id"
  //     valueName = "name"
  //
  //  In practice, `children` is a promise returned from an API request.
  //  The options retain the ordering of the initial API response.

  const classes = useStyles();
  const { state, setState, disabled } = useContext(SearchFormContext);

  // `value` is currently selected options, defaulting to none
  let value = state[name] || [];
  // when the state is initially set to a single option, we
  // must convert it to an array
  if (!Array.isArray(value)) value = [value];

  // `options` will be set to an object mapping option keys
  // to option values/labels. If the initial promise data
  // was [{id: 1, name: "a"}, {id: 2, name: "b"}], it will
  // be converted to {1: "a", 2: "b"}.
  const [options, setOptions] = useState({});
  // Because the options are converted to a single object,
  // their ordering is lost. We retain the ordering by creating
  // an array of keys. `orderedKeys` is what the MultiSelect
  // uses for it's list of options, and reads `options` with
  // each key to obtain the displayed value.
  const [orderedKeys, setOrderedKeys] = useState([]);

  // The relative complication of this design is necessary to
  // allow loading search form state from URL parameters, which
  // only contain the options `keyName`.

  useEffect(() => {
    // TODO: This can sometimes cause an unmounted component state update
    //       warning in the console. It can be fixed, but it does not
    //       cause any problems for this component or the app.
    children()
      .then((results) => {
        setOptions(Object.fromEntries(results.map((opt) => [opt[keyName], opt[valueName]])));
        setOrderedKeys(results.map((opt) => opt[keyName]));
      })
      // TODO: add more resilient error handling
      .catch(console.error);
  }, []);

  // user input event handler
  const handleChange = (event, value) => {
    setState((prevState) => ({ ...prevState, [name]: value }));
  };

  // https://material-ui.com/components/autocomplete/
  return (
    <Autocomplete
      multiple
      limitTags={5}
      options={orderedKeys}
      getOptionLabel={(optionKey) => options[optionKey]}
      value={value}
      ChipProps={{ size: "small" }}
      onChange={handleChange}
      className={classes.root}
      disabled={disabled}
      renderInput={(params) => <TextField {...params} variant="outlined" label={label} />}
    />
  );
};

export default MultiSelect;
