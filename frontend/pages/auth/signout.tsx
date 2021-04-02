import { Box, Container, Typography } from "@material-ui/core";
import { useSession } from "next-auth/client";
import React, { FunctionComponent, useEffect } from "react";
import { handleLogout } from "../../auth";
import Layout from "../../components/layout";

const SignOut: FunctionComponent = () => {
  const [session, _loading] = useSession();
  useEffect(() => {
    if (session) {
      handleLogout(session);
    }
  }, [session]);
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
          <Typography className="text-center">Signing out...</Typography>
        </Box>
      </Container>
    </Layout>
  );
};

export default SignOut;
