import { AxiosResponse } from "axios";
import { NextApiHandler, NextApiRequest, NextApiResponse } from "next";
import NextAuth, {
  CallbacksOptions,
  NextAuthOptions,
  PagesOptions,
  Session,
  User as NextAuthUser
} from "next-auth";
import { JWT as NextAuthJWT } from "next-auth/jwt";
import Providers from "next-auth/providers";
import { WithAdditionalParams } from "next-auth/_utils";
import axios from "../../../axios";

const SESSION_TOKEN_COOKIE_NAME = "next-auth.session-token";

const makeDjangoApiUrl = (endpoint) => {
  return `http://django:8000/api${endpoint}`;
};

interface JWT extends NextAuthJWT {
  accessToken: string;
  cookies: Array<string>;
}

interface User extends NextAuthUser {
  accessToken: string;
  refreshToken: string;
  cookies: Array<string>;
}

// https://next-auth.js.org/configuration/providers
const providers = [
  // https://next-auth.js.org/providers/discord
  Providers.Discord({
    clientId: process.env.SOCIAL_AUTH_DISCORD_CLIENT_ID,
    clientSecret: process.env.SOCIAL_AUTH_DISCORD_SECRET,
    scope: 'identify email',
  }),
  // TODO: Enable Facebook login?
  // // https://next-auth.js.org/providers/facebook
  // Providers.Facebook({
  //   clientId: process.env.SOCIAL_AUTH_FACEBOOK_KEY,
  //   clientSecret: process.env.SOCIAL_AUTH_FACEBOOK_SECRET,
  // }),
  // https://next-auth.js.org/providers/google
  Providers.Google({
    clientId: process.env.SOCIAL_AUTH_GOOGLE_KEY,
    clientSecret: process.env.SOCIAL_AUTH_GOOGLE_SECRET,
  }),
  // https://next-auth.js.org/providers/twitter
  Providers.Twitter({
    clientId: process.env.SOCIAL_AUTH_TWITTER_KEY,
    clientSecret: process.env.SOCIAL_AUTH_TWITTER_SECRET,
  }),
  // TODO: Someday, enable troublesome GitHub login?
  // // https://next-auth.js.org/providers/github
  // Providers.GitHub({
  //   clientId: process.env.SOCIAL_AUTH_GITHUB_CLIENT_ID,
  //   clientSecret: process.env.SOCIAL_AUTH_GITHUB_SECRET,
  // }),
  // https://next-auth.js.org/providers/credentials
  Providers.Credentials({
    id: "credentials",
    name: "Credentials",  // name to display on the sign-in form ('Sign in with ____')
    credentials: {  // fields expected to be submitted in the sign-in form
      username: { label: "Username", type: "text", placeholder: "" },
      password: { label: "Password", type: "password" },
    },
    async authorize(credentials) {
      return await authenticateWithCredentials(credentials);
    },
  }),
];

// https://next-auth.js.org/configuration/callbacks
const callbacks: CallbacksOptions = {};

callbacks.signIn = async function signIn(user: User, provider, _data) {
  if (provider.type != 'credentials') {
    switch (provider.provider) {
      case "discord": // https://next-auth.js.org/providers/discord
        break;
      case "facebook": // https://next-auth.js.org/providers/facebook
        break;
      case "github": { // https://next-auth.js.org/providers/github
        // Retrieve email address, if necessary.
        if (!user.email) {
          const emailRes = await fetch('https://api.github.com/user/emails', {
            headers: {'Authorization': `token ${provider.accessToken}`}
          })
          const emails = await emailRes.json();
          if (emails?.length != 0) {
            user.email = emails.find(emails => emails.primary).email;
          }
        }
        break;
      }
      case "google": // https://next-auth.js.org/providers/google
        break;
      case "twitter": // https://next-auth.js.org/providers/twitter
        break;
      default:
        console.error('Unrecognized auth provider:', provider);
        return false;
    }
    user = await authenticateWithSocialMediaAccount(user, provider);
  }
  const allowLogin = user ? true : false;
  if (!allowLogin) {
    console.log('Rejected login.');
  }
  return allowLogin;
};

// https://next-auth.js.org/configuration/callbacks#jwt-callback
callbacks.jwt = async function jwt(token, user?: User, account?, profile?, isNewUser?: boolean) {
  // The arguments user, account, profile and isNewUser are only passed the first time
  // this callback is called on a new session, after the user signs in.
  if (user && account) { // initial sign in
    token.accessToken = user.accessToken;
    token.cookies = user.cookies;
    token.refreshToken = user.refreshToken;
  }
  if (token.cookies) {
    let sessionTokenCookie;
    token.cookies.forEach((cookie) => {
      if (cookie.startsWith(`${SESSION_TOKEN_COOKIE_NAME}=`)) {
        sessionTokenCookie = cookie;
      }
    });
    token.accessTokenExpiry =
      token.accessTokenExpiry ?? Date.parse(sessionTokenCookie.match(/expires=(.+?);/)[1]);
  }
  // Refresh the access token if it is expired.
  if (Date.now() > token.accessTokenExpiry) {
    token = await refreshAccessToken(token);
  }
  return Promise.resolve(token);
};

// https://next-auth.js.org/configuration/callbacks#session-callback
callbacks.session = async function session(session: Session, jwt: JWT) {
  const sessionPlus: WithAdditionalParams<Session> = { ...session };
  if (jwt) {
    const accessToken = jwt.accessToken;
    const cookies = jwt.cookies;
    let sessionTokenCookie;
    cookies.forEach((cookie) => {
      if (cookie.startsWith(`${SESSION_TOKEN_COOKIE_NAME}=`)) {
        sessionTokenCookie = cookie;
      }
    });
    const expiry =
      jwt.accessTokenExpiry ?? Date.parse(sessionTokenCookie.match(/expires=(.+?);/)[1]);
    if (accessToken) {
      sessionPlus.accessToken = accessToken;
      // If the access token is expired, ...
      if (Date.now() > expiry) {
        console.error("Session got an expired access token.");
      }
      sessionPlus.cookies = cookies;
      if (!sessionPlus.user) {
        let userData;
        await axios
          .get(makeDjangoApiUrl("/users/me/"), {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          })
          .then(function (response: AxiosResponse) {
            userData = response.data;
          })
          .catch(function (error) {
            console.error(error);
          });
        sessionPlus.user = userData;
      }
    }
  }
  return sessionPlus;
};

callbacks.redirect = async function redirect(url, baseUrl) {
  url = url.startsWith(baseUrl) ? url : baseUrl;
  // TODO: refactor
  const reactPattern = /\/(entities\/?|other_react_pattern\/?)/;
  if (!url.includes("/auth/redirect/")) {
    if (!reactPattern.test(url)) {
      const path = url.replace(baseUrl, "").replace('/auth/signin', "");
      // Remove duplicate slashes.
      url = `${baseUrl}/auth/redirect/${path}`.replace(/([^:]\/)\/+/g, "$1");
    }
  }
  return url;
};

// https://next-auth.js.org/configuration/pages
const pages: PagesOptions = {
  signIn: "/auth/signin",
  signOut: "/auth/signout",
};

const options: NextAuthOptions = {
  // https://next-auth.js.org/configuration/options#callbacks
  callbacks: callbacks,
  // https://next-auth.js.org/configuration/options#jwt
  jwt: { secret: process.env.SECRET_KEY },
  // https://next-auth.js.org/configuration/pages
  pages: pages,
  // https://next-auth.js.org/configuration/options#providers
  providers: providers,
  // https://next-auth.js.org/configuration/options#secret
  secret: process.env.SECRET_KEY,
  // https://next-auth.js.org/configuration/options#session
  session: { jwt: true },
};

const authHandler: NextApiHandler = (req: NextApiRequest, res: NextApiResponse) => {
  return NextAuth(req, res, options);
};

export default authHandler;

async function authenticateWithCredentials(credentials) {
  const url = makeDjangoApiUrl("/users/auth/login/");
  let user;
  await axios
    .post(url, {
      username: credentials.username,
      password: credentials.password,
    })
    .then(function (response: AxiosResponse) {
      user = response.data["user"];
      if (!user) {
        console.log("Response did not contain user data.");
        return Promise.resolve(null);
      }
      /*
        Attach necessary values to the user object.
        Subsequently, the JWT callback reads these values from the user object
        and attaches them to the token object that it returns.
      */
      user.accessToken = response.data.access_token;
      user.refreshToken = response.data.refresh_token;
      user.cookies = response.headers["set-cookie"];
    })
    .catch(function (error) {
      console.error(`${error}`);
      return Promise.resolve(null);
    });
  return Promise.resolve(user);
}

interface SocialMediaAccountCredentials {
  access_token?: string
  code?: string
  token_secret?: string
  refresh_token?: string
  user: User
}

async function authenticateWithSocialMediaAccount(user: User, provider) {
  const url = makeDjangoApiUrl(`/users/auth/${provider.provider}`);
  const credentials: SocialMediaAccountCredentials = {user: user};
  switch (provider.provider) {
    case "discord": // https://next-auth.js.org/providers/discord
    case "facebook": // https://next-auth.js.org/providers/facebook
    case "github": // https://next-auth.js.org/providers/github
    case "google": // https://next-auth.js.org/providers/google
    case "twitter": // https://next-auth.js.org/providers/twitter
      credentials.access_token = provider.accessToken;
      credentials.refresh_token = provider.refreshToken;
      break;
    default:
      console.error('Unsupported provider:', provider.provider);
      return user;
  }
  await axios
    .post(url, credentials)
    .then(function (response) {
      /*
        Attach necessary values to the user object.
        Subsequently, the JWT callback reads these values from the user object
        and attaches them to the token object that it returns.
      */
      user.accessToken = response.data.access_token;
      user.refreshToken = response.data.refresh_token;
      user.cookies = response.headers["set-cookie"];
    })
    .catch(function (error) {
      // handle error
      console.error(error);
      return Promise.resolve(null);
    });
  return Promise.resolve(user);
}

// https://next-auth.js.org/tutorials/refresh-token-rotation
async function refreshAccessToken(jwt: JWT) {
  /*
    Return a new token with updated `accessToken` and `accessTokenExpiry`.
    If an error occurs, return the old token.  TODO: Add error property?
    jwt contains name, email, accessToken, cookies, refreshToken, accessTokenExpiry, iat, exp.
  */
  console.log("Refreshing access token...");
  await axios
    .post(makeDjangoApiUrl("/users/auth/token/refresh/"), {
      refresh: jwt.refreshToken,
    })
    .then(function (response: AxiosResponse) {
      if (response.data.access && response.data.access_token_expiration) {
        console.log("Refreshed access token.");
        /*
          Example response:
          {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOzODQzLCJqdGkiOngly0HZdG66ic",
            "access_token_expiration": "2021-03-25T20:24:03.605165Z"
          }
        */
        const accessTokenExpiry = Date.parse(response.data.access_token_expiration);
        const cookies = response.headers["set-cookie"];
        if (Date.now() > accessTokenExpiry) {
          console.error("New access token is already expired.");
        }
        jwt = {
          ...jwt,
          // Fall back to old refresh token if necessary.
          refreshToken: response.data.refresh_token ?? jwt.refreshToken,
          accessToken: response.data.access,
          accessTokenExpiry: accessTokenExpiry,
          cookies: cookies,
          iat: Date.now() / 1000,
          exp: accessTokenExpiry / 1000,
        };
      } else if (response.data.code === "token_not_valid") {
        console.log("Refresh token expired.");
        /*
          Example response:
          {
            "detail": "Token is invalid or expired",
            "code": "token_not_valid"
          }
        */
      } else {
        console.error(`Failed to parse response: ${response.data}`);
      }
    })
    .catch(function (error) {
      console.error(`Failed to refresh auth token due to error:\n${error}`);
    });
  return jwt;
}
