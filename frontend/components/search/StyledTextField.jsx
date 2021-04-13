import { TextField } from "@material-ui/core";

export default function StyledTextField(props) {
  // Mui TextField with some default props.
  return <TextField fullWidth variant={"outlined"} size={"small"} {...props} />;
}
