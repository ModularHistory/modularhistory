import { Box, Button } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { signOut, useSession } from 'next-auth/client';
import React, { useEffect } from "react";
import { djangoLogoutUrl, handleLogout } from "../../auth";
import axios from "../../axios";
import Layout from "../../components/layout";

export default function SignOut() {
  const [session] = useSession();

  const logout = (e) => {
    e.preventDefault()
    handleLogout(session);
  }

  return (
    <Layout title={"Sign out"}>
      <Container>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          m={5}
          p={5}
          flexDirection="column"
        >
          <Button variant="outlined" color="primary" onClick={logout}>
            Sign Out
          </Button>
        </Box>
      </Container>
    </Layout>
  );
}

export function PagelessSignOut() {
  const [session] = useSession();
  const handleLogout = () => {
    // Sign out of the back end.
    axios
    .post(djangoLogoutUrl, {refresh: session.refreshToken}, {
      headers: {
        Authorization: `Bearer ${session.expiresaccessToken}`,
      }
    })
    .then(function () {
      document.cookie = `next-auth.callback-url=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
      document.cookie = `next-auth.session-token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
    })
    .catch(function (error) {
      console.error(`Failed to sign out due to error:\n${error}`);
      throw new Error(`${error}`);
    });
    // Sign out of the front end.
    signOut();
    // To trigger the event listener we save some random data into the `logout` key
    window.localStorage.setItem("logout", Date.now()); // new
  }
  useEffect(() => {
    handleLogout();
    window.location.replace(window.location.origin);
  }, [])
  return null;
}
