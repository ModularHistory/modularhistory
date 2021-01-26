import Container from "@material-ui/core/Container";
import { providers } from 'next-auth/client';
import React from 'react';
import Layout from "../../components/layout";

const BASE_URL = 'http://dev';

{/* <div class="signin">
  <div class="provider">
  <hr>
  <form action="http://dev/api/auth/callback/credentials" method="POST">
    <input type="hidden" name="csrfToken" value="2d58f12d0104b1e1ba41a01ca423e2fb00defa6337c448d643f46eca647eab0d">
    <div>
      <label for="input-username-for-credentials-provider">Username</label>
      <input name="username" id="input-username-for-credentials-provider" type="text" value="" placeholder="">
    </div>
    <div>
      <label for="input-password-for-credentials-provider">Password</label>
      <input name="password" id="input-password-for-credentials-provider" type="password" value="" placeholder="">
    </div>
    <div>
      <label for="input-csrf_token-for-credentials-provider">CSRF_Token</label>
      <input name="csrf_token" id="input-csrf_token-for-credentials-provider" type="hidden" value="" placeholder="">
    </div>
    <button type="submit">Sign in with Credentials</button>
  </form>
</div> */}


export default function SignIn({ providers }) {
  return (
    <Layout title={"Entities"}>
      <Container>
        <div className="text-center">
          {Object.values(providers).map(provider => (
            <div key={provider.name} className="provider">
              {/* <button onClick={() => signIn(provider.id)}>Sign in with {provider.name}</button> */}
              <form action={`${BASE_URL}/api/auth/signin/${provider.name}`} method="POST">
                <input type="hidden" name="csrfToken" value="2d58f12d0104b1e1ba41a01ca423e2fb00defa6337c448d643f46eca647eab0d" />
                <input type="hidden" name="callbackUrl" value="http://dev" />
                <button type="submit" class="button">
                  Sign in with {provider.name}
                </button>
              </form>
            </div>
          ))}
        </div>
      </Container>
    </Layout>
  )
}

export async function getStaticProps(context) {
    return {
        props: {
            providers: await providers(context)
        }, // passed to the page component as props
    }
  }
