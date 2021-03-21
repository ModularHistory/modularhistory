import axios, { AxiosResponse } from "axios";
import { NextApiHandler, NextApiRequest, NextApiResponse } from "next";
import NextAuth, { Callbacks, InitOptions, User as NextAuthUser } from "next-auth";
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
}

// https://next-auth.js.org/configuration/providers
const providers = [
  // TODO: https://next-auth.js.org/providers/discord
  Providers.Discord({
    clientId: process.env.SOCIAL_AUTH_DISCORD_CLIENT_ID,
    clientSecret: process.env.SOCIAL_AUTH_DISCORD_SECRET
  }),
  // TODO: https://next-auth.js.org/providers/facebook
  Providers.Facebook({
    clientId: process.env.SOCIAL_AUTH_FACEBOOK_KEY,
    clientSecret: process.env.SOCIAL_AUTH_FACEBOOK_SECRET,
  }),
  // TODO: https://next-auth.js.org/providers/google
  Providers.Google({
    clientId: process.env.SOCIAL_AUTH_GOOGLE_KEY,
    clientSecret: process.env.SOCIAL_AUTH_GOOGLE_SECRET,
  }),
  // TODO: https://next-auth.js.org/providers/twitter
  Providers.Twitter({
    clientId: process.env.SOCIAL_AUTH_TWITTER_KEY,
    clientSecret: process.env.SOCIAL_AUTH_TWITTER_SECRET,
  }),
  // TODO: https://next-auth.js.org/providers/github
  Providers.GitHub({
    clientId: process.env.SOCIAL_AUTH_GITHUB_KEY,
    clientSecret: process.env.SOCIAL_AUTH_GITHUB_SECRET,
  }),
  // TODO: https://next-auth.js.org/providers/credentials
  Providers.Credentials({
    id: "credentials",
    // The name to display on the sign-in form (i.e., 'Sign in with ...')
    name: "Credentials",
    // The fields expected to be submitted in the sign-in form
    credentials: {
      username: { label: "Username", type: "text", placeholder: "" },
      password: { label: "Password", type: "password" },
      // djangoCsrfToken: { label: "CSRF Token", type: "text" },  // TODO
    },
    async authorize(credentials) {
      console.log(">>>>>>>>>>>>>>>>>>>>>>>");
      // const token = cookies(context).csrftoken || "";
      const url = makeDjangoApiUrl("/users/auth/login/");
      // axios.defaults.headers[djangoCsrfCookieName] = credentials.djangoCsrfToken || null;  // TODO
      // TODO: Use state?
      // See https://github.com/iMerica/dj-rest-auth/blob/master/demo/react-spa/src/App.js
      let user;
      await axios
        .post(url, {
          username: credentials.username,
          password: credentials.password,
        })
        .then(function (response: AxiosResponse) {
          // handle success
          user = response.data["user"];
          if (!user) {
            throw new Error(`${response}`);
          }
          user.accessToken = response.data.access_token;
          user.refreshToken = response.data.refresh_token;
          return Promise.resolve(user);
        })
        .catch(function (error) {
          // handle error
          console.error(error);
          throw new Error(error);
        });
      return Promise.resolve(user);
    }
  }),
];

// https://next-auth.js.org/configuration/callbacks
const callbacks: Callbacks = {};

callbacks.signIn = async function signIn(user: User, provider, data) {
  console.log("\nSigning in via", provider.type, "...");
  console.log("\nsignIn.user: ", user, "\n");
  let accessToken: string;
  if (provider.id === "credentials") {
    /*
      Coming from the credentials provider, `data` is of the following form:
      {
        csrfToken: 'example',
        username: 'example',
        password: 'example'
      }
    */
    accessToken = user.accessToken;
    // refreshToken = user.refreshToken;
    // accessToken = await signInWithCredentials(data.username, data.password);
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
  }
  user.accessToken = accessToken;
  return true;
};

// https://next-auth.js.org/configuration/callbacks#jwt-callback
callbacks.jwt = async function jwt(token, user?: User, account?, profile?, isNewUser?: boolean) {
  // The arguments user, account, profile and isNewUser are only passed the first time 
  // this callback is called on a new session, after the user signs in.
  console.log("\ncallbacks.jwt -->");
  if (isNewUser) {
    console.log(`Signing in ${user} for the first time.`)
  }
  if (user) {
    console.log('Setting access token ...');
    token.accessToken = user.accessToken;
  }
  return Promise.resolve(token);
};

callbacks.session = async function session(session, user: User) {
  console.log("\ncallbacks.session -->");
  const accessToken = user.accessToken;
  session.accessToken = accessToken;
  let userData;
  const url = makeDjangoApiUrl("/users/me");
  await axios
    .get(url, {
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
      throw new Error(error);
    });
  session.user = userData;
  console.log(session);
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

const options: InitOptions = {
  // https://next-auth.js.org/configuration/options#callbacks
  callbacks: callbacks,
  // https://next-auth.js.org/configuration/options#jwt
  jwt: {secret: process.env.SECRET_KEY},
  // https://next-auth.js.org/configuration/pages
  pages: {
    signIn: "/auth/signin",
  },
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
  return response
}

async function signInWithCredentials (username, password) {
  const url = makeDjangoApiUrl("/users/auth/login/");
  let accessToken;
  await axios
    .post(url, {
      username: username,
      password: password,
    })
    .then(function (response: AxiosResponse) {
      // handle success
      if (!response) {
        throw new Error(`${response}`);
      }
      accessToken = response.data.access_token;
    })
    .catch(function (error) {
      // handle error
      console.error(error);
      throw new Error(error);
    });
  return accessToken;
}
