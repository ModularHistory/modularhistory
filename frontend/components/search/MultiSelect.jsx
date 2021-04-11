import React, {useContext, useState, useEffect} from 'react';
import Autocomplete from '@material-ui/lab/Autocomplete';
import {makeStyles} from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import {SearchFormContext} from "./SearchForm";

const useStyles = makeStyles({
  root: {
    "& .MuiChip-root": {
      margin: 1,
      fontSize: "11px",
      height: "20px",
      "& .MuiChip-label": {
        paddingLeft: "6px",
        paddingRight: "8px"
      },
      "& .MuiChip-deleteIcon": {
        height: "18px",
        width: "18px",
        marginRight: "2px",
      }
    },
  },
});

export default function MultiSelect({label, name, keyName, valueName, children}) {
  const classes = useStyles();
  const {state, setState, disabled} = useContext(SearchFormContext);
  let value = state[name] || [];
  if (!Array.isArray(value)) value = [value];

  const [options, setOptions] = useState({});
  const [orderedKeys, setOrderedKeys] = useState([]);
  useEffect(() => {
    children()
      .then((results) => {
        setOptions(Object.fromEntries(
          results.map(opt => [opt[keyName], opt[valueName]])
        ));
        setOrderedKeys(
          results.map(opt => opt[keyName])
        );
      })
      .catch(console.error)
  }, [])

  const handleChange = (event, value) => {
    setState((prevState) => ({...prevState, [name]: value}));
  }

  return (
    <div>
      <Autocomplete
        multiple
        limitTags={5}
        options={orderedKeys}
        getOptionLabel={optionKey => options[optionKey]}
        value={value}
        ChipProps={{size: "small"}}
        onChange={handleChange}
        className={classes.root}
        disabled={disabled}
        renderInput={(params) => (
          <TextField {...params}
                     variant="outlined"
                     label={label}
          />
        )}
      />
    </div>
  );
}
