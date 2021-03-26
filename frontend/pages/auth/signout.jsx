import { Box, Button, Typography } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { signOut, useSession } from 'next-auth/client';
import React from "react";
import axios from "../../axios";
import Layout from "../../components/layout";

const logoutUrl = '/api/users/auth/logout/';

export default function SignOut() {
  const [session, loading] = useSession();
  const handleLogout = (e) => {
    e.preventDefault()
    // Sign out of the back end.
    console.log('Trying to log out with token ', session.accessToken);
    axios
    .post(logoutUrl, {refresh: session.refreshToken}, {
      headers: {
        Authorization: `Bearer ${session.expiresaccessToken}`,
      }
    })
    .then(function (response) {
      console.log('logout response: ', response);
      document.cookie = `next-auth.callback-url=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
      document.cookie = `next-auth.session-token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
    })
    .catch(function (error) {
      console.error(`Failed to sign out due to error:\n${error}`);
      throw new Error(`${error}`);
    });
    // Sign out of the front end.
    signOut()
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
          {!loading && session && session.user && (
            <>
              <Typography>Logged in as {session.user.email}</Typography>
              <Button
                variant="outlined"
                color="primary"
                onClick={handleLogout}
              >
                Sign Out
              </Button>
            </>
          )}
        </Box>
      </Container>
    </Layout>
  );
}
