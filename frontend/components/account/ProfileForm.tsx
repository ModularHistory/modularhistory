import axios from "@/axiosWithAuth";
import TextField from "@/components/forms/StyledTextField";
import { Grid } from "@material-ui/core";
import Button from "@material-ui/core/Button";
import { AxiosResponse } from "axios";
import { User } from "next-auth";
import { FC, useState } from "react";

interface ProfileFormProps {
  user: User;
  csrfToken: string;
}

const ProfileForm: FC<ProfileFormProps> = ({ user, csrfToken }: ProfileFormProps) => {
  const [name, setName] = useState(user.name || "");
  const [username, setUsername] = useState(user.username || "");
  const [error, setError] = useState("");
  const handleProfileChange = async (event) => {
    event.preventDefault();
    if (!username) {
      setError("Enter a username.");
    } else {
      await axios
        .patch(`/api/users/${user.username}/`, {
          name,
          username,
        })
        .then(function (response: AxiosResponse) {
          if (response["error"]) {
            setError("Invalid.");
          }
        })
        .catch(function (error) {
          setError(String(error));
          return Promise.resolve(null);
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
            id="username"
            name="username"
            value={username}
            label={"Username"}
            onChange={(event) => setUsername(event.target.value)}
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
