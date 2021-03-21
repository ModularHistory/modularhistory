import { Box, Button, Typography } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { csrfToken, providers, signIn, signOut, useSession } from 'next-auth/client';
import PropTypes from 'prop-types';
import React from "react";
import Layout from "../../components/layout";


const CREDENTIALS_KEY = 'credentials';

export default function SignIn({ providers, csrfToken }) {  // djangoCsrfToken
  const [session, loading] = useSession();
  const credentialsAuthProvider = providers[CREDENTIALS_KEY];
  // Clone the providers object and remove the credentials provider. 
  const socialAuthProviders = JSON.parse(JSON.stringify(providers));
  delete socialAuthProviders[CREDENTIALS_KEY];
  // console.log('>>>> ', djangoCsrfToken);
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
            <>
              <Typography>Logged in as {session.user.email}</Typography>
              <pre>{JSON.stringify(session, null, 2)}</pre>
              <Button
                variant="outlined"
                color="primary"
                onClick={() => signOut()}
              >
                Sign Out
              </Button>
            </>
          )}
          {!loading && !session && (
            <>
              <div key={credentialsAuthProvider.name} className="provider">
                <form method='post' action='/api/auth/callback/credentials'>
                  <input type="hidden" name="csrfToken" value={csrfToken} />
                  <label>
                    Username
                    <input name='username' type='text'/>
                  </label>
                  <label>
                    Password
                    <input name='password' type='password'/>
                  </label>
                  <button type='submit'>Sign in</button>
                </form>
              </div>
              <>
                {Object.values(socialAuthProviders).map(provider => (
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
  // djangoCsrfToken: PropTypes.string
}

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export async function getServerSideProps(context) {
  // const token = cookies(context).csrftoken || "";
  // console.log('>>>getServerSideProps>>> ', token)
  return {
    props: {
      providers: await providers(context),
      csrfToken: await csrfToken(context),
      // djangoCsrfToken: token
    }, // passed to the page component as props
  };
}
