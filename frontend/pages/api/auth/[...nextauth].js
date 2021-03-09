import axios from "axios";
import NextAuth from "next-auth";
import Providers from "next-auth/providers";

const djangoCsrfCookieName = "csrftoken"

// Axios config for DRF requests
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = djangoCsrfCookieName;
axios.defaults.withCredentials = true;

const makeDjangoApiUrl = (endpoint) => {
  return `http://django:8000/api/account${endpoint}`;
};

const providers = [
  // TODO
  // Providers.Discord({
  //   clientId: process.env.SOCIAL_AUTH_DISCORD_KEY,
  //   clientSecret: process.env.SOCIAL_AUTH_DISCORD_SECRET
  // })
  Providers.Facebook({
    clientId: process.env.SOCIAL_AUTH_FACEBOOK_KEY,
    clientSecret: process.env.SOCIAL_AUTH_FACEBOOK_SECRET,
  }),
  Providers.Twitter({
    clientId: process.env.SOCIAL_AUTH_TWITTER_KEY,
    clientSecret: process.env.SOCIAL_AUTH_TWITTER_SECRET,
  }),
  Providers.GitHub({
    clientId: process.env.SOCIAL_AUTH_GITHUB_KEY,
    clientSecret: process.env.SOCIAL_AUTH_GITHUB_SECRET,
  }),
  Providers.Credentials({
    id: "credentials",
    // The name to display on the sign-in form (i.e., 'Sign in with ...')
    name: "Credentials",
    // The fields expected to be submitted in the sign-in form
    credentials: {
      username: { label: "Username", type: "text", placeholder: "" },
      password: { label: "Password", type: "password" },
      // djangoCsrfToken: { label: "CSRF Token", type: "text" },
    },
    async authorize(credentials) {
      console.log("Attempting to authorize");
      // const token = cookies(context).csrftoken || "";
      const url = makeDjangoApiUrl("/auth/login/");
      axios.defaults.headers[djangoCsrfCookieName] = credentials.djangoCsrfToken || null;
      // TODO: Use state?
      // See https://github.com/iMerica/dj-rest-auth/blob/master/demo/react-spa/src/App.js
      const response = await axios
        .post(url, {
          username: credentials.username,
          password: credentials.password,
        })
        .then(function (response) {
          // handle success
          console.log(response);
        })
        .catch(function (error) {
          // handle error
          console.error(error);
        });
      console.log("authorize got response: ", response);
      return Promise.resolve(response["user"] ? response["user"] : null);
    }
  }),
];

const callbacks = {};

async function getTokenFromYourAPIServer(provider, user) {
  const url = makeDjangoApiUrl("/token/obtain");
  const response = await axios
    .post(url, {
      username: credentials.username,
      password: credentials.password,
    })
    .then(function (response) {
      // handle success
      console.log(response);
    })
    .catch(function (error) {
      // handle error
      console.error(error);
    });
  return response
}

callbacks.signIn = async function signIn(user, account, data) {
  console.log("signIn.user: ", user, "\nsignIn.account.provider: ", account.provider, "\nsignIn.data: ", data);
  let accessToken = null;
  if (account.provider === "credentials") {
    console.log('Get token from API server!!!');  // TODO
    accessToken = await getTokenFromYourAPIServer(account.provider, user);
  } else {
    console.log(`Signing in via ${account.provider}`);
    let socialUser;
    switch (account.provider) {
      case "facebook":
        socialUser = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image,
        };
        break;
      case "github":
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
      case "google":
        socialUser = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image,
        };
        break;
      case "twitter":
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
    accessToken = null;  // TODO: await getTokenFromYourAPIServer(account.provider, socialUser);
  }
  // https://getstarted.sh/bulletproof-next/add-social-authentication/7
  user.accessToken = accessToken;
  return true;
};

// https://next-auth.js.org/configuration/callbacks#jwt-callback
callbacks.jwt = async function jwt(token, user) {
  console.log("callbacks.jwt --> ", token, user);
  const isAuthenticated = user ? true : false;
  if (isAuthenticated) {
    token = { accessToken: user.accessToken };
    // token.auth_time = Math.floor(Date.now() / 1000)
  }
  return Promise.resolve(token);
};

callbacks.session = async function session(session, token) {
  console.log("callbacks.session --> ", session, token);
  session.accessToken = token.accessToken;
  const user = null;  // await getUserFromApi(session.accessToken);  // TODO
  if (!user) {
    return null;
  }
  session.user = user;
  return Promise.resolve(session);
};

const options = {
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
};

export default (req, res) => NextAuth(req, res, options)
