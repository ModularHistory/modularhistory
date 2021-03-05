import Container from "@material-ui/core/Container";
import { csrfToken, providers, signIn } from 'next-auth/client';
import PropTypes from 'prop-types';
import React from "react";
import Layout from "../../components/layout";
import cookies from 'next-cookies';

const CREDENTIALS_KEY = 'credentials';

export default function SignIn({ providers, csrfToken }) {  // djangoCsrfToken
  const credentialsAuthProvider = providers[CREDENTIALS_KEY] || null;
  const socialAuthProviders = providers;
  if (credentialsAuthProvider) {
    console.log('Credentials provider is enabled.');
    delete socialAuthProviders[CREDENTIALS_KEY];
  } else {
    console.log('Credentials provider is not enabled.');
  }
  // console.log('>>>> ', djangoCsrfToken);
  return (
    <Layout title={"Sign in"}>
      <Container>
        <div className="text-center">
          {credentialsAuthProvider && (
            <div key={credentialsAuthProvider.name} className="provider">
              <form method='post' action='/api/auth/callback/credentials'>
                <input type="hidden" name="csrfToken" value={csrfToken} />
                <label>
                  Username
                  <input name='username' type='text'/>
                </label>
                <label>
                  Password
                  <input name='password' type='text'/>
                </label>
                <button type='submit'>Sign in</button>
              </form>
            </div>
          )}
          <>
            {Object.values(providers).map(provider => (
              <div key={provider.name} className="provider">
                <button onClick={() => signIn(provider.id)}>Sign in with {provider.name}</button>
              </div>
            ))}
          </>
        </div>
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
