import {useContext} from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Chip from '@material-ui/core/Chip';
import {SearchFormContext} from "./SearchForm";

const useStyles = makeStyles((theme) => ({
  formControl: {
    "& .MuiSelect-root": {
      backgroundColor: "white",
    },
  },
  chips: {
    display: 'flex',
    flexWrap: 'wrap',
  },
  chip: {
    margin: 1,
    fontSize: "11px",
    height: "24px",
  },
  noLabel: {
    marginTop: theme.spacing(3),
  },
}));

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

const names = [
  'Oliver Hansen',
  'Van Henry',
  'April Tucker',
  'Ralph Hubbard',
  'Omar Alexander',
  'Carlos Abbott',
  'Miriam Wagner',
  'Bradley Wilkerson',
  'Virginia Andrews',
  'Kelly Snyder',
];

export default function EntitySelect({label, name}) {
  const classes = useStyles();
  const [state, setState] = useContext(SearchFormContext);
  const value = state[name] || [];

  return (
    <FormControl className={classes.formControl} variant={"outlined"} fullWidth>
      <InputLabel id="entity-selection">{label}</InputLabel>
      <Select
        labelId="entity-selection"
        multiple
        name={name}
        value={value}
        onChange={setState}
        input={<Input id="select-multiple-chip"/>}
        renderValue={(selected) => (
          <div className={classes.chips}>
            {selected.map((value) => (
              <Chip key={value} label={value} className={classes.chip}/>
            ))}
          </div>
        )}
        MenuProps={MenuProps}
      >
        {names.map((name) => (
          <MenuItem key={name} value={name}>
            {name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
