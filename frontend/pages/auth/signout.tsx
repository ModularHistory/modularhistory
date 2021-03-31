import { Box, Button } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { useSession } from "next-auth/client";
import React, { FunctionComponent, useEffect } from "react";
import { handleLogout } from "../../auth";
import Layout from "../../components/layout";

const SignOut: FunctionComponent = () => {
  const [session] = useSession();

  const logout = (e) => {
    e.preventDefault();
    handleLogout(session);
  };

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

export default SignOut;

export const PagelessSignOut: FunctionComponent = () => {
  const [session, loading] = useSession();
  useEffect(() => {
    if (!loading) {
      handleLogout(session);
    }
  }, [loading]);
  return null;
}
