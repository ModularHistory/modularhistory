import Container from "@material-ui/core/Container";
import { providers, signIn } from 'next-auth/client';
import PropTypes from 'prop-types';
import React from "react";
import Layout from "../../components/layout";


// TODO: https://create-react-app.dev/docs/proxying-api-requests-in-development
const BASE_URL = "http://modularhistory.dev.net";
const CREDENTIALS_KEY = 'credentials';

export default function SignIn({ providers }) {
  // const providers = await providers(context);
  console.log('>>>>>>>>>>> ', providers);
  const credentialsAuthProvider = providers[CREDENTIALS_KEY] || null;
  const socialAuthProviders = providers;
  if (credentialsAuthProvider) {
    delete socialAuthProviders[CREDENTIALS_KEY];
  } else {
    console.log('Credentials provider is not enabled.');
  }
  return (
    <Layout title={"Entities"}>
      <Container>
        <div className="text-center">
          {credentialsAuthProvider && (
            <div key={credentialsAuthProvider.name} className="provider">
              <form method='post' action='/api/auth/callback/credentials'>
                {/* <input name='csrfToken' type='hidden' defaultValue={csrfToken}/> */}
                <input
                  type="hidden"
                  name="csrfToken"
                  value="asdfjkl;"
                />
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
          {Object.values(providers).map(provider => (
            <div key={provider.name}>
              <button onClick={() => signIn(provider.id)}>Sign in with {provider.name}</button>
            </div>
          ))}
        </div>
      </Container>
    </Layout>
  );
}

// https://reactjs.org/docs/typechecking-with-proptypes.html
SignIn.propTypes = {
  providers: PropTypes.object,
}

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export async function getServerSideProps(context) {
  return {
    props: {
      providers: await providers(context),
      // socialAuthProviders,
      // credentialsAuthProvider
    }, // passed to the page component as props
  };
}
