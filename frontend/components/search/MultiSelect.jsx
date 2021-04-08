/* eslint-disable no-use-before-define */
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
      "& .MuiChip-deleteIcon" : {
        height: "18px",
        width: "18px",
        marginRight: "2px",
      }
    },
  },
});

export default function MultiSelect({label, name, children}) {
  const classes = useStyles();
  const [state, _, setState] = useContext(SearchFormContext);
  let value = state[name] || [];
  if (!Array.isArray(value)) value = [value];

  const [selectItems, setSelectItems] = useState([]);
  useEffect(() => {
    children().then(setSelectItems)
  }, [])

  const handleChange = (event, value, reason) => {
    setState((prevState) => ({...prevState, [name]: value}));
  }

  return (
    <div>
      <Autocomplete
        multiple
        limitTags={5}
        options={Object.keys(entities)}
        getOptionLabel={(option) => entities[option]}
        value={value}
        ChipProps={{size: "small"}}
        onChange={handleChange}
        className={classes.root}
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

const entities = {
  7: "Joseph Smith",
  8: "Brigham Young",
};