import { Box, Button, Paper, TextField } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import Alert from '@material-ui/lab/Alert';
import { csrfToken, providers, signIn, signOut, useSession } from "next-auth/client";
import { useRouter } from 'next/router';
import PropTypes from "prop-types";
import React from "react";
import { DiscordLoginButton, FacebookLoginButton, GithubLoginButton, GoogleLoginButton, TwitterLoginButton } from "react-social-login-buttons";
import Layout from "../../components/layout";


const CREDENTIALS_KEY = "credentials";
const SOCIAL_LOGIN_BUTTONS = {
  facebook: FacebookLoginButton,
  discord: DiscordLoginButton,
  google: GoogleLoginButton,
  twitter: TwitterLoginButton,
  github: GithubLoginButton,
};

export default function SignIn({ providers, csrfToken }) {
  const [session, loading] = useSession();
  const router = useRouter();
  const credentialsAuthProvider = providers[CREDENTIALS_KEY];
  const socialAuthLoginComponents = [];
  let SocialLoginButton;
  Object.entries(providers).forEach(
    ([, provider]) => {
      if (provider.id === CREDENTIALS_KEY) { return null }
      SocialLoginButton = SOCIAL_LOGIN_BUTTONS[provider.id];
      socialAuthLoginComponents.push(
        <div key={provider.name} className="provider">
          <SocialLoginButton onClick={() => signIn(provider.id)}>
            Sign in with {provider.name}
          </SocialLoginButton>
        </div>
      )
    }
  );
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
          {!loading && session?.user && (
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
                {router.query?.error && (
                  <>
                    <Alert severity="error">Invalid credentials.</Alert>
                    <br />
                  </>
                )}
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
              <hr />
              <>
                {socialAuthLoginComponents}
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
