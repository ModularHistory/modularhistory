import { handleLogout } from "@/auth";
import Layout from "@/components/Layout";
import { Box, Container, Typography } from "@mui/material";
import { useSession } from "next-auth/react";
import { NextSeo } from "next-seo";
import { FunctionComponent, useEffect } from "react";

const SignOut: FunctionComponent = () => {
  const { data: session } = useSession();
  useEffect(() => {
    if (session) {
      handleLogout(session);
    }
  }, [session]);
  return (
    <Layout>
      <NextSeo title={"Sign out"} noindex />
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
