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
          console.log("user: ", response.data.user);
          console.log("access_token: ", response.data.access_token);
          console.log("refresh_token: ", response.data.refresh_token);
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

const callbacks: Callbacks = {};

callbacks.signIn = async function signIn(user: User, provider, data) {
  console.log("\nSigning in via ", provider.type)
  console.log("\nsignIn.data: ", data);
  let accessToken: string;
  if (provider.id === "credentials") {
    const url = makeDjangoApiUrl("/users/auth/login/");
    await axios
      .post(url, {
        username: data.username,
        password: data.password,
      })
      .then(function (response: AxiosResponse) {
        // handle success
        if (!user) {
          throw new Error(`${response}`);
        }
        console.log("user: ", response.data.user);
        console.log("access_token: ", response.data.access_token);
        console.log("refresh_token: ", response.data.refresh_token);
        accessToken = response.data.access_token;
      })
      .catch(function (error) {
        // handle error
        console.error(error);
        throw new Error(error);
      });
  } else {
    let socialUser;
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
  // https://getstarted.sh/bulletproof-next/add-social-authentication/7
  user.accessToken = accessToken;
  return true;
};

// https://next-auth.js.org/configuration/callbacks#jwt-callback
callbacks.jwt = async function jwt(token, user: User) {
  console.log("callbacks.jwt --> ", token, user);
  const isAuthenticated = user ? true : false;
  if (isAuthenticated) {
    token = { accessToken: user.accessToken };
    // token.auth_time = Math.floor(Date.now() / 1000)
  }
  return Promise.resolve(token);
};

callbacks.session = async function session(session, user: User) {
  console.log("callbacks.session --> ", session, user);
  session.accessToken = user.accessToken;
  let userData;
  const url = makeDjangoApiUrl("/users/me");
  await axios
    .get(url, {})
    .then(function (response: AxiosResponse) {
      // handle success
      console.log("response: ", response.data);
      userData = response.data.user;
    })
    .catch(function (error) {
      // handle error
      console.error(error);
      throw new Error(error);
    });
  session.user = userData;
  return Promise.resolve(session);
};

const options: InitOptions = {
  providers: providers,
  session: {
    jwt: true
  },
  jwt: {
    secret: process.env.SECRET_KEY
  },
  callbacks: callbacks,
  // TODO: https://next-auth.js.org/configuration/pages
  pages: {
    signIn: "/auth/signin",
    // signOut: '/auth/signout'
  },
  // secret: process.env.SECRET_KEY,  // TODO?
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
