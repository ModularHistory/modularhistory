import { BooleanFieldProps } from "@/components/cms/fields/types";
import { InputLabel } from "@material-ui/core";
import Checkbox from "@material-ui/core/Checkbox";
import { FC, useState } from "react";

const BooleanField: FC<BooleanFieldProps> = (props: BooleanFieldProps) => {
  const [value, setValue] = useState(props.value);
  return (
    <div>
      <InputLabel htmlFor={props.name} style={{ marginLeft: "1.5rem" }}>
        {props.verboseName}
      </InputLabel>
      <Checkbox
        id={props.name}
        checked={value === true}
        disabled={props.editable === false}
        onChange={(event) => setValue(event.target.checked)}
      />
    </div>
  );
};

export default BooleanField;
