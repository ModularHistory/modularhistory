import axios from "@/axiosWithAuth";
import TextField from "@/components/forms/StyledTextField";
import { Grid } from "@mui/material";
import Button from "@mui/material/Button";
import { User } from "next-auth";
import { FC, FormEventHandler, useState } from "react";

interface ProfileFormProps {
  user: User;
  csrfToken: string;
}

const ProfileForm: FC<ProfileFormProps> = ({ user, csrfToken }: ProfileFormProps) => {
  const [name, setName] = useState(user.name || "");
  const [handle, setHandle] = useState(user.handle || "");
  const [error, setError] = useState("");
  const handleProfileChange: FormEventHandler = async (event) => {
    event.preventDefault();
    if (!handle) {
      setError("Enter a handle.");
    } else {
      await axios
        .patch(`/api/users/${user.handle}/`, {
          name,
          handle,
        })
        .catch((error) => {
          setError(String(error));
        });
    }
  };
  return (
    <form method="post" onSubmit={handleProfileChange}>
      {csrfToken && <input type="hidden" name="csrfToken" value={csrfToken} />}
      {error && <p className="text-center">{error}</p>}
      <Grid container spacing={2}>
        <Grid item sm={12} md={6}>
          <TextField
            id="name"
            name="name"
            value={name}
            label={"Name"}
            onChange={(event) => setName(event.target.value)}
          />
        </Grid>
        <Grid item sm={12} md={6}>
          <TextField
            id="handle"
            name="handle"
            value={handle}
            label={"Username"}
            onChange={(event) => setHandle(event.target.value)}
          />
        </Grid>
        <Grid item md={12}>
          <Button type="submit" color="primary" variant="outlined">
            {"Save"}
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default ProfileForm;
