import { handleLogout } from "@/auth";
import axios from "@/axiosWithAuth";
import SocialLogin from "@/components/account/SocialLogin";
import Layout from "@/components/Layout";
import { Alert, Box, Button, Divider, Grid, Paper, TextField } from "@mui/material";
import Container from "@mui/material/Container";
import { GetServerSideProps } from "next";
import { getCsrfToken, getProviders, signIn, useSession } from "next-auth/react";
import { NextSeo } from "next-seo";
import Link from "next/link";
import { useRouter } from "next/router";
import { FormEventHandler, FunctionComponent, useEffect, useState } from "react";

interface RegistrationProps {
  providers: Awaited<ReturnType<typeof getProviders>>;
  csrfToken: Awaited<ReturnType<typeof getCsrfToken>>;
}

const RegistrationPage: FunctionComponent<RegistrationProps> = ({
  providers,
  csrfToken,
}: RegistrationProps) => {
  const router = useRouter();
  const callbackUrl = Array.isArray(router.query?.callbackUrl)
    ? router.query.callbackUrl[0]
    : router.query?.callbackUrl;
  const { data: session, status } = useSession();
  const loading = status === "loading";
  const [redirecting, setRedirecting] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirmation, setPasswordConfirmation] = useState("");
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [redirectUrl, setRedirectUrl] = useState(callbackUrl || process.env.BASE_URL || "");
  useEffect(() => {
    if (router.query?.error) {
      setErrors({ _: [`${router.query?.error}`] });
    }
  }, [router.query?.error]);
  useEffect(() => {
    if (!redirectUrl) {
      setRedirectUrl(window.location.origin);
    }
    if (redirecting) {
      // TODO: Refactor to centralize the regex test in some other module.
      // Use Next.js router to redirect to a React page,
      // or use window.location to redirect to a non-React page.
      // Note: window.location is safe in any case.
      if (/(\/django_url_pattern1\/?|\/django_url_pattern2\/?)/.test(redirectUrl)) {
        window.location.replace(redirectUrl);
      } else {
        router.push(redirectUrl);
      }
    }
  }, [redirecting, router, redirectUrl]);
  const handleCredentialLogin: FormEventHandler = async (event) => {
    event.preventDefault();
    await axios
      .post("/api/users/auth/registration/", {
        email,
        password,
        passwordConfirmation,
      })
      .then(function () {
        signIn("credentials", {
          username: email,
          password: password,
          callbackUrl: redirectUrl,
          // https://next-auth.js.org/getting-started/client#using-the-redirect-false-option
          redirect: false,
        });
        setRedirecting(true);
      })
      .catch(function (error) {
        // eslint-disable-next-line no-console
        setErrors(error.response?.data?.error);
      });
  };
  if (loading) {
    return null;
  }
  return (
    <Layout>
      <NextSeo
        title={"Sign up"}
        canonical={"/auth/registration"}
        description={"Register for a free ModularHistory account."}
      />
      <Container>
        <Box m={"auto"} p={4} style={{ maxWidth: "40rem" }}>
          {!!Object.keys(errors).length && !redirecting && (
            <>
              <Alert severity="error">
                {Object.entries(errors || {}).map(([prop, value]) => {
                  return (
                    <p className="error-message" key={prop}>
                      {value}
                    </p>
                  );
                })}
              </Alert>
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
                  Sign up
                </h1>
                <form method="post" onSubmit={handleCredentialLogin}>
                  {csrfToken && <input type="hidden" name="csrfToken" value={csrfToken} />}
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <Grid container spacing={2}>
                        <Grid item xs={12}>
                          <TextField
                            id="email"
                            name="email"
                            label="Email address"
                            variant="outlined"
                            size="small"
                            fullWidth
                            onChange={(event) => setEmail(event.target.value)}
                            required
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
                            required
                          />
                        </Grid>
                        <Grid item xs={12}>
                          <TextField
                            id="password-confirmation"
                            name="passwordConfirmation"
                            label="Confirm password"
                            variant="outlined"
                            type="password"
                            size="small"
                            fullWidth
                            onChange={(event) => setPasswordConfirmation(event.target.value)}
                            required
                          />
                        </Grid>
                      </Grid>
                    </Grid>
                    <Grid item xs={12}>
                      <Button fullWidth type="submit" variant="contained">
                        Register
                      </Button>
                    </Grid>
                    <Grid item xs={12}>
                      <p>
                        {"Already have an account? "}
                        <Link href="/auth/registration">Sign in</Link>.
                      </p>
                    </Grid>
                  </Grid>
                </form>
                <Divider style={{ width: "100%", marginTop: "2rem", marginBottom: "2rem" }} />
                <SocialLogin providers={providers} callbackUrl={redirectUrl} onError={setErrors} />
              </div>
            ))}
        </Box>
      </Container>
    </Layout>
  );
};

export default RegistrationPage;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  return {
    props: {
      providers: await getProviders(),
      csrfToken: (await getCsrfToken(context)) || null,
    }, // passed to the page component as props
  };
};
