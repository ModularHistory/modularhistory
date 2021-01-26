import axios from 'axios';
import Cookies from 'cookies';
import NextAuth from 'next-auth';
import Providers from 'next-auth/providers';

// Axios config for DRF requests
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.withCredentials = true

const server = "http://django:8000";
const API_BASE = `${server}/api/account`;

const makeDjangoApiUrl = (endpoint) => {
  return API_BASE + endpoint;
}

const getUser = (username, password, csrf_token) => {
  const url = makeDjangoApiUrl("/login/");
  console.log('getUser ', url);
  axios.defaults.headers[axios.defaults.xsrfHeaderName] = csrf_token;
  return axios.post(url, { username, password }).then(function (response) {
    // handle success
    console.log(response);
  }).catch(function (error) {
    // handle error
    console.error(error);
  })
};

const fetchTokenPair = (username, password) => {
  const url = makeDjangoApiUrl("/token/obtain/");
  console.log('fetchTokenPair ', url);
  return fetch(url, {
    method: "POST",
    body: JSON.stringify({ username, password }),
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include"
  });
};

// const refreshToken = () => {
//   const url = makeDjangoApiUrl("/token/refresh/");
//   return fetch(url, {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     credentials: "include"
//   });
// };

// async function fetchUser(token) {
//   const url = makeDjangoApiUrl("/me/")
//   const params = {
//     method: "GET",
//     headers: {
//       Authorization: `Bearer ${token}`,
//     },
//   }
//   return fetch(url, params);
// }

const providers = [
  Providers.Facebook({
    clientId: process.env.SOCIAL_AUTH_FACEBOOK_KEY,
    clientSecret: process.env.SOCIAL_AUTH_FACEBOOK_SECRET
  }),
  Providers.Twitter({
    clientId: process.env.SOCIAL_AUTH_TWITTER_KEY,
    clientSecret: process.env.SOCIAL_AUTH_TWITTER_SECRET
  }),
  Providers.GitHub({
    clientId: process.env.SOCIAL_AUTH_GITHUB_KEY,
    clientSecret: process.env.SOCIAL_AUTH_GITHUB_SECRET
  }),
  Providers.Credentials({
    // The name to display on the sign-in form (i.e., 'Sign in with ...')
    name: 'Credentials',
    // The fields expected to be submitted in the sign-in form
    credentials: {
      username: { label: "Username", type: "text", placeholder: "" },
      password: { label: "Password", type: "password" },
      csrf_token: { label: "CSRF_Token", type: "hidden" }
    },
    authorize: async (credentials) => {
      // Look up the user based on the credentials supplied
      console.log('Attempting to authorize');
      let response;
      response = await getUser(credentials.username, credentials.password, csrf_token);
      console.log('authorize got response: ', response);
      const user = response['user'] ? response['user'] : null;
      return Promise.resolve(user);
    }
  }),
]

const callbacks = {}

callbacks.signIn = async function signIn(user, account, data) {
  console.log('signIn.user: ', user);
  console.log('signIn.account: ', account);
  console.log('signIn.data: ', data);
  if (account.provider === 'credentials') {
    user.accessToken = await getTokenFromYourAPIServer(account.provider, user);
  } else {
    let socialUser;
    switch (account.provider) {
      case 'facebook':
        socialUser = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image
        }
        break;
      case 'github':
        socialUser = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image
        }
        break;
      case 'google':
        socialUser = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image
        }
        break;
      case 'twitter':
        socialUser = {
          id: data.id,
          login: data.login,
          name: data.name,
          avatar: user.image
        }
        break;
      default:
        return false;
    }
  }
  // user.accessToken = await getTokenFromYourAPIServer(account.provider, socialUser);
  return true;
}

// https://next-auth.js.org/configuration/callbacks#jwt-callback
callbacks.jwt = async function jwt(token, user) {
  console.log('callbacks.jwt');
  console.log('jwt.token', token);
  console.log('jwt.user', user);
  const isAuthenticated = (user) ? true : false;
  if (isAuthenticated) {
    token = { accessToken: user.accessToken }
    // token.auth_time = Math.floor(Date.now() / 1000)
  }
  return Promise.resolve(token);
}

callbacks.session = async function session(session, token) {
  console.log('callbacks.session');
  console.log('session.session', session);
  console.log('session.token', token);
  session.accessToken = token.accessToken
  // session.user = getUserFromApi(session.accessToken);
  return Promise.resolve(session);
}

const options = {
  providers: providers,
  callbacks: callbacks,
  // TODO: https://next-auth.js.org/configuration/pages
  pages: {
    signIn: '/auth/signin',
    // signOut: '/auth/signout'
  }
  // A database is optional, but required to persist accounts in a database
  // database: process.env.DATABASE_URL,
}

export default (req, res) => {
  const cookies = new Cookies(req, res);
  const csrf_cookie = cookies.get('csrftoken');
  console.log('HEEEEEYYYYYYY');
  console.log(csrf_cookie);
  NextAuth(req, res, options);
}

// async function fetchUser(): Promise<AxiosResponse> {
//   const url = makeDjangoApiUrl("/me/");
//   return axios.get(url);
// }

//   const login = async (username: string, password: string): Promise<Response> => {
//     const response = await fetchToken(username, password);
//     if (response.ok) {
//       const tokenData = await response.json();
//       handleNewToken(tokenData);
//       await initUser(tokenData.access);
//     } else {
//       setIsAuthenticated(false);
//       setLoading(true);
//       // Let the page handle the error
//     }
//     return response;
//   };
