import { Box, Button, Divider, Paper, TextField } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import Grid from "@material-ui/core/Grid";
import Alert from '@material-ui/lab/Alert';
import axios from "axios";
import { csrfToken, providers, signIn, signOut, useSession } from "next-auth/client";
import { Providers } from 'next-auth/providers';
import { useRouter } from 'next/router';
import React, { FunctionComponent, useEffect, useState } from "react";
// https://www.npmjs.com/package/react-social-login-buttons
import { DiscordLoginButton, FacebookLoginButton, GithubLoginButton, GoogleLoginButton, TwitterLoginButton } from "react-social-login-buttons";
import { NEXT_AUTH_CSRF_COOKIE_NAME } from '../../auth';
import Layout from "../../components/layout";


axios.defaults.xsrfCookieName = NEXT_AUTH_CSRF_COOKIE_NAME;
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const CREDENTIALS_KEY = "credentials";
const SOCIAL_LOGIN_BUTTONS = {
  facebook: FacebookLoginButton,
  discord: DiscordLoginButton,
  google: GoogleLoginButton,
  twitter: TwitterLoginButton,
  github: GithubLoginButton,
};

interface SignInFormProps {
  csrfToken: string
}

export const SignInForm: FunctionComponent<SignInFormProps> = ({ csrfToken }: SignInFormProps) => {
  const router = useRouter();
  const [error, setError] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const callbackUrl = `${router.query?.callbackUrl}`;
  const redirectUrl = callbackUrl || process.env.BASE_URL;
  const handleSubmit = async (event) => {
    event.preventDefault();
    console.log(username, password);
    if (!username || !password) {
      setError("You must enter your username and password.")
    } else {
      console.log('Posting credentials...');
      let response;
      try {
        response = await signIn('credentials',
          {
            username,
            password,
            callbackUrl: redirectUrl,
            // https://next-auth.js.org/getting-started/client#using-the-redirect-false-option
            redirect: false
          }
        );
      } catch (error) {
        response = {error: `${error}`}
      }
      if (response['error']) {
        // Response contains `error`, `status`, and `url` (intended redirect url).
        setError("Invalid credentials.");
      } else {
        // Response contains `ok` and `url` (intended redirect url).
        window.location.replace(`${response.url ?? redirectUrl ?? window.location.origin}`);
      }
    }
  };
  useEffect(() => {
    if (router.query?.error) {
      setError(`${router.query?.error}`);
    }
  }, []);
  return (
    <form method="post" onSubmit={handleSubmit}>
      {error && (
        <>
          <Alert severity="error">{error}</Alert>
          <br />
        </>
      )}
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
                onChange={event => setUsername(event.target.value)}
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
                onChange={event => setPassword(event.target.value)}
              />
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <Button color="primary" fullWidth type="submit" variant="contained">
            Sign in
          </Button>
        </Grid>
      </Grid>
    </form>
  )
}

interface SignInProps {
  providers: Providers
  csrfToken: string
}

const SignIn: FunctionComponent<SignInProps> = ({ providers, csrfToken }: SignInProps) => {
  const [session, loading] = useSession();
  const credentialsAuthProvider = providers[CREDENTIALS_KEY];
  const socialAuthLoginComponents = [];
  let SocialLoginButton;
  Object.entries(providers).forEach(
    ([, provider]) => {
      if (provider.id === CREDENTIALS_KEY) { return null }
      SocialLoginButton = SOCIAL_LOGIN_BUTTONS[provider.id];
      socialAuthLoginComponents.push(
        <div key={provider.name} className="provider">
          <SocialLoginButton style={{minWidth: "245px"}} onClick={() => signIn(provider.id)}>
            Sign in with {provider.name}
          </SocialLoginButton>
        </div>
      )
    }
  );
  return (
    <Layout title={"Sign in"}>
      <Container>
        <h1 className="page-title text-center" style={{margin: "1rem"}}>Sign in</h1>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          m={2}
          p={5}
          flexDirection="column"
        >
          {!loading && session?.user && (
            <Paper className="p-4 text-center">
              <p className="lead">
                You are logged in as <strong>{session.user.username || session.user.email}</strong>.
              </p>
              <br />
              <Button variant="outlined" color="primary" size="large" onClick={() => signOut()}>
                Sign Out
              </Button>
            </Paper>
          )}
          {!loading && !session && (
            <>
              <div key={credentialsAuthProvider.name}>
                <SignInForm csrfToken={csrfToken} />
              </div>
              <Divider style={{width: "100%", margin: "2rem"}} />
              {socialAuthLoginComponents}
            </>
          )}
        </Box>
      </Container>
    </Layout>
  );
}

export default SignIn;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export async function getServerSideProps(context) {
  return {
    props: {
      providers: await providers(),
      csrfToken: await csrfToken(context),
    }, // passed to the page component as props
  };
}
