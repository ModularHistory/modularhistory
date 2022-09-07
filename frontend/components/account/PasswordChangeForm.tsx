import { makeDjangoApiUrl } from "@/auth";
import axios from "@/axiosWithAuth";
import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import Input from "@mui/material/Input";
import InputLabel from "@mui/material/InputLabel";
import { FC, FormEventHandler, useState } from "react";

interface PasswordChangeFormProps {
  csrfToken: string;
}

const PasswordChangeForm: FC<PasswordChangeFormProps> = ({
  csrfToken,
}: PasswordChangeFormProps) => {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const handlePasswordChange: FormEventHandler = async (event) => {
    event.preventDefault();
    if (!oldPassword) {
      setError("Enter your current password.");
    } else if (!newPassword) {
      setError("Enter your new password.");
    } else if (!confirmPassword) {
      setError("Confirm your new password.");
    } else {
      await axios
        .post(makeDjangoApiUrl("/users/auth/password/change/"), {
          old_password: oldPassword,
          new_password1: newPassword,
          new_password2: confirmPassword,
        })
        .catch(function (error) {
          setError(String(error));
        });
    }
  };
  return (
    <form method="post" onSubmit={handlePasswordChange}>
      {csrfToken && <input type="hidden" name="csrfToken" value={csrfToken} />}
      {error && <p className="text-center">{error}</p>}
      <FormControl fullWidth margin="dense">
        <InputLabel htmlFor="password-current">{"Current password"}</InputLabel>
        <Input
          id="password-current"
          name="currentPass"
          type="password"
          onChange={(event) => setOldPassword(event.target.value)}
        />
      </FormControl>
      <FormControl fullWidth margin="dense">
        <InputLabel htmlFor="password-new">{"New password"}</InputLabel>
        <Input
          id="password-new"
          name="newPass"
          type="password"
          onChange={(event) => setNewPassword(event.target.value)}
        />
      </FormControl>
      <FormControl fullWidth margin="dense">
        <InputLabel htmlFor="password-confirm">{"Confirm new password"}</InputLabel>
        <Input
          id="password-confirm"
          name="confirmPass"
          type="password"
          onChange={(event) => setConfirmPassword(event.target.value)}
        />
      </FormControl>
      <Button type="submit" color="primary">
        {"Reset Password"}
      </Button>
    </form>
  );
};

export default PasswordChangeForm;
