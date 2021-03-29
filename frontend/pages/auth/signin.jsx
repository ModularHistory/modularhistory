import { Box, Button, Paper, TextField } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import { csrfToken, providers, signIn, signOut, useSession } from "next-auth/client";
import PropTypes from "prop-types";
import React from "react";
import Layout from "../../components/layout";

const CREDENTIALS_KEY = "credentials";

export default function SignIn({ providers, csrfToken }) {
  const [session, loading] = useSession();
  const credentialsAuthProvider = providers[CREDENTIALS_KEY];
  // Clone the providers object and remove the credentials provider.
  const socialAuthProviders = JSON.parse(JSON.stringify(providers));
  delete socialAuthProviders[CREDENTIALS_KEY];
  return (
    <Layout title={"Sign in"}>
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
            <Paper className="p-4 text-center">
              <p className="lead">
                You are logged in as <strong>{session.user.email}</strong>.
              </p>
              <br />
              <Button variant="outlined" color="primary" size="large" onClick={() => signOut()}>
                Sign Out
              </Button>
            </Paper>
          )}
          {!loading && !session && (
            <>
              <div key={credentialsAuthProvider.name} className="provider">
                <form method="post" action="/api/auth/callback/credentials">
                  <input type="hidden" name="csrfToken" value={csrfToken} />
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <Grid container spacing={2}>
                        <Grid item xs={12}>
                          <TextField
                            id="username"
                            name="username"
                            label="Username or email address"
                            variant="outlined"
                            size="small"
                            fullWidth
                          />
                        </Grid>
                        <Grid item xs={12}>
                          <TextField
                            id="password"
                            name="password"
                            label="Password"
                            variant="outlined"
                            type="password"
                            size="small"
                            fullWidth
                          />
                        </Grid>
                      </Grid>
                    </Grid>
                    <Grid item xs={12}>
                      <Button color="primary" fullWidth type="submit" variant="contained">
                        Log in
                      </Button>
                    </Grid>
                  </Grid>
                </form>
              </div>
              <>
                {Object.values(socialAuthProviders).map((provider) => (
                  <div key={provider.name} className="provider">
                    <Button variant="outlined" onClick={() => signIn(provider.id)}>
                      Sign in with {provider.name}
                    </Button>
                  </div>
                ))}
              </>
            </>
          )}
        </Box>
      </Container>
    </Layout>
  );
}

// https://reactjs.org/docs/typechecking-with-proptypes.html
SignIn.propTypes = {
  providers: PropTypes.object,
  csrfToken: PropTypes.string,
};

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export async function getServerSideProps(context) {
  return {
    props: {
      providers: await providers(context),
      csrfToken: await csrfToken(context),
    }, // passed to the page component as props
  };
}
