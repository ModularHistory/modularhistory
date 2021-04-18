import { AxiosResponse } from "axios";
import { NextApiHandler, NextApiRequest, NextApiResponse } from "next";
import NextAuth, {
  CallbacksOptions,
  NextAuthOptions,
  PagesOptions,
  Session,
  User,
} from "next-auth";
import { JWT } from "next-auth/jwt";
import Providers from "next-auth/providers";
import { WithAdditionalParams } from "next-auth/_utils";
import { removeServerSideCookies } from "../../../auth";
import axios from "../../../axiosWithAuth";

const ACCESS_TOKEN_COOKIE_NAME = "access-token";

const makeDjangoApiUrl = (endpoint) => {
  return `http://django:8000/api${endpoint}`;
};

// https://next-auth.js.org/configuration/providers
const providers = [
  // https://next-auth.js.org/providers/discord
  Providers.Discord({
    clientId: process.env.SOCIAL_AUTH_DISCORD_CLIENT_ID,
    clientSecret: process.env.SOCIAL_AUTH_DISCORD_SECRET,
    scope: "identify email",
  }),
  // https://next-auth.js.org/providers/facebook
  Providers.Facebook({
    clientId: process.env.SOCIAL_AUTH_FACEBOOK_KEY,
    clientSecret: process.env.SOCIAL_AUTH_FACEBOOK_SECRET,
  }),
  // https://next-auth.js.org/providers/google
  Providers.Google({
    clientId: process.env.SOCIAL_AUTH_GOOGLE_CLIENT_ID,
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
    name: "Credentials", // name to display on the sign-in form ('Sign in with ____')
    credentials: {
      // fields expected to be submitted in the sign-in form
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
  if (provider.type != "credentials") {
    switch (provider.provider) {
      case "discord": // https://next-auth.js.org/providers/discord
        break;
      case "facebook": // https://next-auth.js.org/providers/facebook
        break;
      case "github": {
        // https://next-auth.js.org/providers/github
        // Retrieve email address, if necessary.
        if (!user.email) {
          const emailRes = await fetch("https://api.github.com/user/emails", {
            headers: { Authorization: `token ${provider.accessToken}` },
          });
          const emails = await emailRes.json();
          if (emails?.length != 0) {
            user.email = emails.find((emails) => emails.primary).email;
          }
        }
        break;
      }
      case "google": // https://next-auth.js.org/providers/google
        break;
      case "twitter": // https://next-auth.js.org/providers/twitter
        break;
      default:
        console.error("Unrecognized auth provider:", provider);
        return false;
    }
    user = await authenticateWithSocialMediaAccount(user, provider);
  }
  const allowLogin = user.error ? false : true;
  if (!allowLogin) {
    console.debug("Rejected login.");
  }
  return allowLogin;
};

// https://next-auth.js.org/configuration/callbacks#jwt-callback
callbacks.jwt = async function jwt(token, user?: User, account?, profile?, isNewUser?: boolean) {
  // The arguments user, account, profile and isNewUser are only passed the first time
  // this callback is called on a new session, after the user signs in.
  if (user && account) {
    // initial sign in
    token.accessToken = user.accessToken;
    token.accessTokenExpiry = user.accessTokenExpiry;
    token.refreshToken = user.refreshToken;
    token.sessionIdCookie = user.sessionIdCookie;
    token.clientSideCookies = user.clientSideCookies;
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
    if (jwt.sessionIdCookie) {
      sessionPlus.sessionIdCookie = jwt.sessionIdCookie;
    }
    if (accessToken) {
      const clientSideCookies = jwt.clientSideCookies;
      const expiry = jwt.accessTokenExpiry;
      sessionPlus.accessToken = accessToken;
      // If the access token is expired, ...
      if (Date.now() > expiry) {
        console.error("Session got an expired access token.");
      }
      sessionPlus.clientSideCookies = clientSideCookies;
      // TODO: Refactor? The point of this is to only make the request when necessary.
      if (!sessionPlus.user?.username) {
        // Replace the session's `user` attribute (containing only name, image, and
        // a couple other fields) with full user details from the Django API.
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
            if (error.response?.data) {
              console.error(error.response.data);
            }
            // return Promise.reject(error);
            return null;
          });
        sessionPlus.user = userData;
      }
    }
  }
  return sessionPlus;
};

callbacks.redirect = async function redirect(url, baseUrl) {
  url = url.startsWith(baseUrl) ? url : baseUrl;
  const reactPagesDoNotNeedToHitTheRedirectPage = false;
  // Strip /auth/signin from the redirect URL if necessary,
  // so that the user is instead redirected to the homepage.
  const path = url.replace(baseUrl, "").replace("/auth/signin", "");
  // Determine whether the redirect URL is to a React or to a non-React page.
  const reactPattern = /(\/?$|\/entities\/?|\/search\/?|\/occurrences\/?|\/quotes\/?)/;
  if (reactPattern.test(url) && reactPagesDoNotNeedToHitTheRedirectPage) {
    // If redirecting to a React page,
    // Strip /auth/redirect from the redirect URL if necessary.
    if (url.includes("/auth/redirect/")) {
      url = url.replace("/auth/redirect", "");
    }
  } else {
    // If redirecting to a non-React page,
    // Add /auth/redirect to the redirect URL if necessary.
    // This will cause the user to first be routed to the "redirect page," where
    // Next.js can set or remove cookies before routing the user to the callback URL.
    if (!url.includes("/auth/redirect/")) {
      url = `${baseUrl}/auth/redirect/${path}`;
      // Remove duplicate slashes.
      url = url.replace(/([^:]\/)\/+/g, "$1");
    }
  }
  return url;
};

// https://next-auth.js.org/configuration/pages
const pages: PagesOptions = {
  error: "/auth/signin",
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
        console.debug("Response did not contain user data.");
        return Promise.resolve(null);
      }
      /*
        Attach necessary values to the user object.
        Subsequently, the JWT callback reads these values from the user object
        and attaches them to the token object that it returns.
      */
      user.accessToken = response.data.access_token;
      user.refreshToken = response.data.refresh_token;
      const cookies = response.headers["set-cookie"];
      cookies.forEach((cookie) => {
        if (cookie.startsWith(`${ACCESS_TOKEN_COOKIE_NAME}=`)) {
          user.accessTokenExpiry = Date.parse(cookie.match(/expires=(.+?);/)[1]);
        } else if (cookie.startsWith(`sessionid=`)) {
          user.sessionIdCookie = cookie;
        }
      });
      user.clientSideCookies = removeServerSideCookies(cookies);
    })
    .catch(function (error) {
      console.error(`${error}`);
      return Promise.resolve(null);
    });
  return Promise.resolve(user);
}

interface SocialMediaAccountCredentials {
  access_token?: string;
  code?: string;
  token_secret?: string;
  refresh_token?: string;
  user: User;
}

async function authenticateWithSocialMediaAccount(user: User, provider) {
  const url = makeDjangoApiUrl(`/users/auth/${provider.provider}`);
  const credentials: SocialMediaAccountCredentials = { user: user };
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
      console.error("Unsupported provider:", provider.provider);
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
      user.clientSideCookies = response.headers["set-cookie"];
    })
    .catch(function (error) {
      user.error = `${error}`;
      console.error("Attached error to user: ", error);
    });
  return Promise.resolve(user);
}

// https://next-auth.js.org/tutorials/refresh-token-rotation
async function refreshAccessToken(jwt: JWT) {
  /*
    Return a new token with updated `accessToken` and `accessTokenExpiry`.
    If an error occurs, return the old token.  TODO: Add error property?
    jwt contains name, email, accessToken, clientSideCookies, refreshToken, accessTokenExpiry, iat, exp.
  */
  await axios
    .post(makeDjangoApiUrl("/users/auth/token/refresh/"), {
      refresh: jwt.refreshToken,
    })
    .then(function (response: AxiosResponse) {
      if (response.data.access && response.data.access_token_expiration) {
        console.debug("Refreshed access token.");
        /*
          Example response:
          {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOzODQzLCJqdGkiOngly0HZdG66ic",
            "access_token_expiration": "2021-03-25T20:24:03.605165Z"
          }
        */
        const accessTokenExpiry = Date.parse(response.data.access_token_expiration);
        const clientSideCookies = removeServerSideCookies(response.headers["set-cookie"]);
        if (Date.now() > accessTokenExpiry) {
          console.error("New access token is already expired.");
        }
        jwt = {
          ...jwt,
          // Fall back to old refresh token if necessary.
          refreshToken: response.data.refresh_token ?? jwt.refreshToken,
          accessToken: response.data.access,
          accessTokenExpiry: accessTokenExpiry,
          clientSideCookies: clientSideCookies,
          iat: Date.now() / 1000,
          exp: accessTokenExpiry / 1000,
        };
      } else if (response.data.code === "token_not_valid") {
        console.debug("Refresh token expired.");
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
