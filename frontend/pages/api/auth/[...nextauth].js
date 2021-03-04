import axios from "axios";
import NextAuth from "next-auth";
import Providers from "next-auth/providers";

// Axios config for DRF requests
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.withCredentials = true;

const makeDjangoApiUrl = (endpoint) => {
  return `http://django:8000/api/account${endpoint}`;
};

const providers = [
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
    // The name to display on the sign-in form (i.e., 'Sign in with ...')
    name: "Credentials",
    // The fields expected to be submitted in the sign-in form
    credentials: {
      username: { label: "Username", type: "text", placeholder: "" },
      password: { label: "Password", type: "password" },
      csrf_token: { type: "hidden" },
    },
    authorize: async (credentials) => {
      // Look up the user based on the credentials supplied
      console.log("Attempting to authorize");
      const url = makeDjangoApiUrl("/login/");
      const csrf_token = null; // TODO
      axios.defaults.headers[axios.defaults.xsrfHeaderName] = csrf_token;
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
    },
  }),
];

const callbacks = {};

callbacks.signIn = async function signIn(user, account, data) {
  console.log("signIn.user: ", user, "\nsignIn.account: ", account, "\nsignIn.data: ", data);
  if (account.provider === "credentials") {
    console.log('Get token from API server!!!');  // TODO
    // user.accessToken = await getTokenFromYourAPIServer(account.provider, user);
  } else {
    let user;
    switch (account.provider) {
      case "facebook":
        user = {
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
        user = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image,
        };
        break;
      case "google":
        user = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image,
        };
        break;
      case "twitter":
        user = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image,
        };
        break;
      default:
        return false;
    }
  }
  // https://getstarted.sh/bulletproof-next/add-social-authentication/7
  user.accessToken = null;  // TODO: await getTokenFromYourAPIServer(account.provider, socialUser);
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
