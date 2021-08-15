import { handleLogout } from "@/auth";
import Layout from "@/components/Layout";
import { Box, Button, Divider, Grid, Paper, TextField } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import Alert from "@material-ui/lab/Alert";
import { GetServerSideProps } from "next";
import { csrfToken, providers, signIn, useSession } from "next-auth/client";
import { useRouter } from "next/router";
import React, { FunctionComponent, useEffect, useState } from "react";
// https://www.npmjs.com/package/react-social-login-buttons
import {
  DiscordLoginButton,
  FacebookLoginButton,
  GithubLoginButton,
  GoogleLoginButton,
  TwitterLoginButton,
} from "react-social-login-buttons";

const CREDENTIALS_KEY = "credentials";
const SOCIAL_LOGIN_BUTTONS = {
  facebook: FacebookLoginButton,
  discord: DiscordLoginButton,
  google: GoogleLoginButton,
  twitter: TwitterLoginButton,
  github: GithubLoginButton,
};

interface Provider {
  id: string;
  name: string;
}

interface SignInProps {
  providers: Provider[];
  csrfToken: string;
}

const SignIn: FunctionComponent<SignInProps> = ({ providers, csrfToken }: SignInProps) => {
  const router = useRouter();
  const [session, loading] = useSession();
  const [redirecting, setRedirecting] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const callbackUrl = `${router.query?.callbackUrl}`;
  const redirectUrl = callbackUrl || process.env.BASE_URL;
  useEffect(() => {
    if (router.query?.error) {
      setError(`${router.query?.error}`);
    }
  }, [router.query?.error]);
  useEffect(() => {
    if (redirecting) {
      const url = redirectUrl ?? window.location.origin;
      // TODO: Refactor to centralize the regex test in some other module.
      // Use Next.js router to redirect to a React page,
      // or use window.location to redirect to a non-React page.
      // Note: window.location is safe in any case.
      if (/(\/django_url_pattern1\/?|\/django_url_pattern2\/?)/.test(url)) {
        window.location.replace(url);
      } else {
        router.push(url);
      }
    }
  }, [redirecting, router, redirectUrl]);
  const handleCredentialLogin = async (event) => {
    event.preventDefault();
    if (!username || !password) {
      setError("You must enter your username and password.");
    } else {
      let response;
      try {
        response = await signIn("credentials", {
          username,
          password,
          callbackUrl: redirectUrl,
          // https://next-auth.js.org/getting-started/client#using-the-redirect-false-option
          redirect: false,
        });
      } catch (error) {
        response = { error: `${error}` };
      }
      if (response["error"]) {
        // Response contains `error`, `status`, and `url` (intended redirect url).
        setError("Invalid credentials.");
      } else {
        // Response contains `ok` and `url` (intended redirect url).
        setRedirecting(true);
      }
    }
  };
  const handleSocialLogin = async (provider_id: string) => {
    try {
      signIn(provider_id, { callbackUrl });
    } catch (error) {
      setError(`${error}`);
    }
  };
  const socialAuthLoginComponents = [];
  let SocialLoginButton;
  if (providers) {
    Object.entries(providers).forEach(([, provider]) => {
      if (provider.id === CREDENTIALS_KEY) {
        return null;
      }
      SocialLoginButton = SOCIAL_LOGIN_BUTTONS[provider.id];
      socialAuthLoginComponents.push(
        <SocialLoginButton
          key={provider.name}
          style={{ minWidth: "245px", maxWidth: "245px" }}
          onClick={() => handleSocialLogin(provider.id)}
        >
          Sign in with {provider.name}
        </SocialLoginButton>
      );
    });
  }
  if (loading) {
    return null;
  }
  return (
    <Layout title={"Sign in"}>
      <Container>
        <Box m={"auto"} p={4} style={{ maxWidth: "40rem" }}>
          {error && !redirecting && (
            <>
              <Alert severity="error">{error}</Alert>
              <br />
            </>
          )}
          {session?.user && !redirecting && (
            <Paper className="p-4 text-center">
              <p className="lead">
                You are logged in as <strong>{session.user.email}</strong>.
              </p>
              <br />
              <Button
                variant="outlined"
                color="primary"
                size="large"
                onClick={() => handleLogout(session)}
              >
                Sign Out
              </Button>
            </Paper>
          )}
          {redirecting ||
            (!session?.user && (
              <div id="sign-in">
                <h1 className="page-title text-center" style={{ margin: "1rem" }}>
                  Sign in
                </h1>
                <form method="post" onSubmit={handleCredentialLogin}>
                  {csrfToken && <input type="hidden" name="csrfToken" value={csrfToken} />}
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
                            onChange={(event) => setUsername(event.target.value)}
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
                            onChange={(event) => setPassword(event.target.value)}
                          />
                        </Grid>
                      </Grid>
                    </Grid>
                    <Grid item xs={12}>
                      <Button fullWidth type="submit" variant="contained">
                        Sign in
                      </Button>
                    </Grid>
                  </Grid>
                </form>
                <Divider style={{ width: "100%", marginTop: "2rem", marginBottom: "2rem" }} />
                {(!!socialAuthLoginComponents.length && (
                  <Grid id="social-sign-in" container justifyContent="center">
                    {socialAuthLoginComponents}
                  </Grid>
                )) || <p className="text-center">Other sign-in options are unavailable.</p>}
              </div>
            ))}
        </Box>
      </Container>
    </Layout>
  );
};

export default SignIn;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  return {
    props: {
      providers: await providers(),
      csrfToken: (await csrfToken(context)) || null,
    }, // passed to the page component as props
  };
};
