import { TextField, TextFieldProps } from "@mui/material";
import { FC } from "react";

const StyledTextField: FC<TextFieldProps> = (props: TextFieldProps) => {
  // Mui TextField with some default props.
  return <TextField fullWidth variant={"outlined"} size={"small"} {...props} />;
};

export default StyledTextField;
