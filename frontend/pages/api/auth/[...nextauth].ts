import axios, { AxiosResponse } from "axios";
import { NextApiHandler, NextApiRequest, NextApiResponse } from "next";
import NextAuth, { CallbacksOptions, NextAuthOptions, PagesOptions, Session as NextAuthSession, User as NextAuthUser } from "next-auth";
import Providers from "next-auth/providers";

const djangoCsrfCookieName = "csrftoken"

// Axios config for DRF requests
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = djangoCsrfCookieName;
axios.defaults.withCredentials = true;

const makeDjangoApiUrl = (endpoint) => {
  return `http://django:8000/api${endpoint}`;
};

interface User extends NextAuthUser {
  accessToken: string
  refreshToken: string
  cookies: Array<string>
  error: string
}
interface Session extends NextAuthSession {
  cookies: Array<string>
  error: string
}

// https://next-auth.js.org/configuration/providers
const providers = [
  // TODO: https://next-auth.js.org/providers/discord
  // TODO: https://modularhistory.atlassian.net/browse/MH-136
  // Providers.Discord({
  //   clientId: process.env.SOCIAL_AUTH_DISCORD_CLIENT_ID,
  //   clientSecret: process.env.SOCIAL_AUTH_DISCORD_SECRET
  // }),
  // // TODO: https://next-auth.js.org/providers/facebook
  // Providers.Facebook({
  //   clientId: process.env.SOCIAL_AUTH_FACEBOOK_KEY,
  //   clientSecret: process.env.SOCIAL_AUTH_FACEBOOK_SECRET,
  // }),
  // // TODO: https://next-auth.js.org/providers/google
  // Providers.Google({
  //   clientId: process.env.SOCIAL_AUTH_GOOGLE_KEY,
  //   clientSecret: process.env.SOCIAL_AUTH_GOOGLE_SECRET,
  // }),
  // // TODO: https://next-auth.js.org/providers/twitter
  // Providers.Twitter({
  //   clientId: process.env.SOCIAL_AUTH_TWITTER_KEY,
  //   clientSecret: process.env.SOCIAL_AUTH_TWITTER_SECRET,
  // }),
  // // TODO: https://next-auth.js.org/providers/github
  // Providers.GitHub({
  //   clientId: process.env.SOCIAL_AUTH_GITHUB_KEY,
  //   clientSecret: process.env.SOCIAL_AUTH_GITHUB_SECRET,
  // }),
  // TODO: https://next-auth.js.org/providers/credentials
  Providers.Credentials({
    id: "credentials",
    // The name to display on the sign-in form (i.e., 'Sign in with ...')
    name: "Credentials",
    // The fields expected to be submitted in the sign-in form
    credentials: {
      username: { label: "Username", type: "text", placeholder: "" },
      password: { label: "Password", type: "password" },
    },
    async authorize(credentials) {
      const url = makeDjangoApiUrl("/users/auth/login/");
      // TODO: Use state? See https://github.com/iMerica/dj-rest-auth/blob/master/demo/react-spa/src/App.js.
      let user;
      await axios
        .post(url, {
          username: credentials.username,
          password: credentials.password,
        })
        .then(function (response: AxiosResponse) {
          console.log('Authenticated user successfully.');
          user = response.data["user"];
          if (!user) {
            throw new Error(`${response}`);
          }
          // Attach necessary values to the user object.
          // Subsequently, the JWT callback reads these values from the user object 
          // and attaches them to the token object it returns.
          user.accessToken = response.data.access_token;
          user.refreshToken = response.data.refresh_token;
          user.cookies = response.headers['set-cookie'];
          return Promise.resolve(user);
        })
        .catch(function (error) {
          console.error(`Failed to authenticate due to error:\n${error}`);
          throw new Error(`${error}`);
        });
      return Promise.resolve(user);
    }
  }),
];

// https://next-auth.js.org/tutorials/refresh-token-rotation#server-side
async function refreshAccessToken(token) {
  /**
   * Return a new token with updated `accessToken` and `accessTokenExpires`. 
   * If an error occurs, return the old token with an error property.
  */
  console.log('Refreshing access token ...');
  await axios
  .post(makeDjangoApiUrl("/users/auth/token/refresh/"), {
    refresh: "aklsjdlkfjasldf"
  })
  .then(function (response: AxiosResponse) {
    /*
      If the refresh token was invalid, the API responds:
      {"detail": "Token is invalid or expired", "code": "token_not_valid"}
    */
    console.log('Refreshed auth token successfully.');
    const refreshedTokens = response.data;
    return {
      ...token,
      accessToken: refreshedTokens.access_token,
      accessTokenExpires: Date.now() + refreshedTokens.expires_in * 1000,
      // Fall back to old refresh token if necessary.
      refreshToken: refreshedTokens.refresh_token ?? token.refreshToken,
    };
  })
  .catch(function (error) {
    console.error(`Failed to refresh auth token due to error:\n${error}`);
    throw error;
    // return {
    //   ...token,
    //   error: "RefreshAccessTokenError",
    // };
  });
  
  // const url =
  //   "https://oauth2.googleapis.com/token?" +
  //   new URLSearchParams({
  //     client_id: process.env.GOOGLE_CLIENT_ID,
  //     client_secret: process.env.GOOGLE_CLIENT_SECRET,
  //     grant_type: "refresh_token",
  //     refresh_token: token.refreshToken,
  //   });

  // const response = await fetch(url, {
  //   headers: {
  //     "Content-Type": "application/x-www-form-urlencoded",
  //   },
  //   method: "POST",
  // });
}

// https://next-auth.js.org/configuration/callbacks
const callbacks: CallbacksOptions = {};

callbacks.signIn = async function signIn(user: User, provider, data) {
  console.log('');
  console.log("\nSigning in via", provider.type, "...");
  console.log("\nsignIn.user: ", user, "\n");
  let accessToken: string;
  let refreshToken: string;
  let cookies: Array<string>;
  if (provider.id === "credentials") {
    /*
      Coming from the credentials provider, `data` is of this form:
      {
        csrfToken: 'example',
        username: 'example',
        password: 'example'
      }
    */
    accessToken = user.accessToken;
    refreshToken = user.refreshToken;
    cookies = user.cookies;
  } else {
    let socialUser;
    console.log("\nsignIn.data: ", data);
    switch (provider.id) {
      case "discord":  // https://next-auth.js.org/providers/discord
        socialUser = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image,
        };
        break;
      case "facebook":  // https://next-auth.js.org/providers/facebook
        socialUser = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image,
        };
        break;
      case "github":  // https://next-auth.js.org/providers/github
        // TODO: https://getstarted.sh/bulletproof-next/add-social-authentication/5
        // const emailRes = await fetch('https://api.github.com/user/emails', {
        //   headers: {
        //     'Authorization': `token ${account.accessToken}`
        //   }
        // })
        // const emails = await emailRes.json()
        // const primaryEmail = emails.find(e => e.primary).email;
        // user.email = primaryEmail;
        socialUser = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image,
        };
        break;
      case "google":  // https://next-auth.js.org/providers/google
        socialUser = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image,
        };
        break;
      case "twitter":  // https://next-auth.js.org/providers/twitter
        socialUser = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image,
        };
        break;
      default:
        return false;
    }
    accessToken = accessToken || null;  // TODO: await getTokenFromYourAPIServer(account.provider, socialUser);
    refreshToken = refreshToken || null;  // TODO: await getTokenFromYourAPIServer(account.provider, socialUser);
    cookies = cookies || null;
  }
  user.accessToken = accessToken;
  user.refreshToken = refreshToken;
  user.cookies = cookies;
  console.log('');
  return true;
};

// https://next-auth.js.org/configuration/callbacks#jwt-callback
callbacks.jwt = async function jwt(token, user?: User, account?, profile?, isNewUser?: boolean) {
  // The arguments user, account, profile and isNewUser are only passed the first time 
  // this callback is called on a new session, after the user signs in.
  console.log('');
  console.log('');
  // Initial sign in
  if (user && account) {
    console.log('jwt - account: ', account);
    token.accessToken = user.accessToken || account.accessToken;
    token.cookies = user.cookies;
    token.accessTokenExpires = Date.now() + account.expires_in * 1000;  // TODO
    token.refreshToken = user.refreshToken || account.refresh_token;
  }

  // Return previous token if the access token has not expired yet
  console.log('Checking if token is expired: ', token);
  if (token.accessTokenExpires && Date.now() > token.accessTokenExpires) {
    // Access token has expired, try to update it
    return refreshAccessToken(token);
  }

  console.log(`JWT callback returns token: `, token);
  console.log('^^^^^^^');
  console.log('');
  return Promise.resolve(token);
};

// TODO: https://next-auth.js.org/tutorials/refresh-token-rotation

callbacks.session = async function session(session: Session, user: User) {
  console.log('');
  console.log("callbacks.session -->");
  const accessToken = user.accessToken;
  session.accessToken = accessToken;
  if (user.error) {
    session.error = user.error;
  } else {
    session.cookies = user.cookies;
    let userData;
    await axios
      .get(makeDjangoApiUrl("/users/me/"), {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        }
      })
      .then(function (response: AxiosResponse) {
        // handle success
        userData = response.data;
      })
      .catch(function (error) {
        // handle error
        console.error(error);
      });
    session.user = userData;
  }
  console.log(session);
  console.log('');
  return Promise.resolve(session);
};

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');  // $& means the whole matched string
}

callbacks.redirect = async function redirect(url, baseUrl) {
  const preUrl = url;
  const re = new RegExp(`(\\?callbackUrl=${escapeRegExp(baseUrl)}\\/auth\\/signin)+`);
  url = preUrl.replace(re, `?callbackUrl=${baseUrl}/auth/signin`);
  if (url != preUrl) {
    console.log(`Changed redirect URL from ${preUrl} to ${url}`);
  }
  return url;
}

// https://next-auth.js.org/configuration/pages
const pages: PagesOptions = {
  signIn: "/auth/signin",
}

const options: NextAuthOptions = {
  // https://next-auth.js.org/configuration/options#callbacks
  callbacks: callbacks,
  // https://next-auth.js.org/configuration/options#jwt
  jwt: {secret: process.env.SECRET_KEY},
  // https://next-auth.js.org/configuration/pages
  pages: pages,
  // https://next-auth.js.org/configuration/options#providers
  providers: providers,
  // https://next-auth.js.org/configuration/options#secret
  secret: process.env.SECRET_KEY,
  // https://next-auth.js.org/configuration/options#session
  session: {jwt: true},
};

const authHandler: NextApiHandler = (req: NextApiRequest, res: NextApiResponse) => {
  return NextAuth(req, res, options);
};

export default authHandler;

async function getTokenFromDjangoServer(user: User) {
  const url = makeDjangoApiUrl("/token/obtain");
  const response = "";
  // TODO
  // const response = await axios
  //   .post(url, {
  //     username: credentials.username,
  //     password: credentials.password,
  //   })
  //   .then(function (response) {
  //     // handle success
  //     console.log(response);
  //   })
  //   .catch(function (error) {
  //     // handle error
  //     console.error(error);
  //   });
  return response;
}
