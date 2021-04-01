import { Box } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { useSession } from "next-auth/client";
import React, { FunctionComponent, useEffect } from "react";
import { handleLogout } from "../../auth";
import Layout from "../../components/layout";

const SignOut: FunctionComponent = () => {
  const [session, loading] = useSession();

  useEffect(() => {
    if (!loading) {
      handleLogout(session);
    }
  }, [loading]);

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
          {!loading && (
            <p>
              Signing out...
            </p>
          )}
        </Box>
      </Container>
    </Layout>
  );
}

export default SignOut;

// export const PagelessSignOut: FunctionComponent = () => {
//   const [session, loading] = useSession();
//   useEffect(() => {
//     if (!loading) {
//       handleLogout(session);
//     }
//   }, [loading]);
//   return null;
// }
