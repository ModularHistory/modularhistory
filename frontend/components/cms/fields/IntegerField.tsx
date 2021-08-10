import { IntegerFieldProps } from "@/components/cms/fields/types";
import { MenuItem, TextField } from "@material-ui/core";
import React, { FC, useState } from "react";

const IntegerField: FC<IntegerFieldProps> = (props: IntegerFieldProps) => {
  const [value, setValue] = useState(props.value);
  if (props.choices) {
    return (
      <TextField
        id={props.name}
        name={props.name}
        value={value}
        label={props.verboseName}
        onChange={(event) => setValue(Number.parseInt(event.target.value))}
        select
      >
        {props.choices.map((choice) => (
          <MenuItem key={choice[0]} selected={value === choice[0]} value={choice[0]}>
            {choice[1]}
          </MenuItem>
        ))}
      </TextField>
    );
  } else {
    return (
      <TextField
        id={props.name}
        name={props.name}
        value={value}
        label={props.verboseName}
        onChange={(event) => setValue(Number.parseInt(event.target.value))}
        disabled={props.editable === false}
      />
    );
  }
};

export default IntegerField;
