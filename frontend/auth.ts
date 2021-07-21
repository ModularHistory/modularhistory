import { AxiosResponse } from "axios";
import { Account, Session, User } from "next-auth";
import { signIn, signOut } from "next-auth/client";
import { JWT } from "next-auth/jwt";
import { Router } from "next/router";
import axios from "./axiosWithAuth";

export const DJANGO_CSRF_COOKIE_NAME = "csrftoken";
const ACCESS_TOKEN_COOKIE_NAME = "access-token";
export const NEXT_AUTH_CSRF_COOKIE_NAME = "next-auth.csrf-token";
export const AUTH_COOKIES = [
  "next-auth.session-token",
  "next-auth.callback-url",
  ACCESS_TOKEN_COOKIE_NAME,
  "refresh-token",
  "sessionid",
];

export const DJANGO_LOGOUT_URL = "/api/users/auth/logout/";
export const LOGIN_PAGE_PATH = "/auth/signin";
export const AUTH_REDIRECT_PATH = "/auth/redirect";

export interface Credentials {
  username: string;
  password: string;
}

export const makeDjangoApiUrl = (endpoint: string): string => {
  return `http://django:8000/api${endpoint}`;
};

export const handleLogin = (router: Router): void => {
  // If not already on the sign-in page, initiate the sign-in process.
  // (This prevents messing up the callbackUrl by reloading the sign-in page.)
  if (router.pathname != "/auth/signin") {
    signIn();
  }
};

export const handleLogout = (session: Session): void => {
  // Sign out of the back end.
  if (session) {
    axios
      .post(
        DJANGO_LOGOUT_URL,
        { refresh: session.refreshToken },
        {
          headers: {
            Authorization: `Bearer ${session.accessToken}`,
          },
        }
      )
      .then(function () {
        // eslint-disable-next-line no-console
        // console.debug("Signed out.");
      })
      .catch(function (error) {
        // eslint-disable-next-line no-console
        console.error(`Failed to sign out due to error: ${error}`);
      });
  }
  // Remove cookies by setting their expiry to a past date.
  AUTH_COOKIES.forEach((cookieName) => {
    document.cookie = `${cookieName}; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
  });
  // Sign out of the front end.
  signOut({ callbackUrl: window.location.pathname });
  // TODO: Save random data to the `logout` key in local storage
  // to trigger the event listener to sign out of any other open windows.
  window.localStorage.setItem("logout", `${Date.now()}`);
};

export const removeServerSideCookies = (cookies: string[]): string[] => {
  // Given an array of cookie strings, remove any HttpOnly cookies.
  // Return the modified array.
  const clientSideCookies = [];
  cookies.forEach((cookie) => {
    if (!cookie.includes("HttpOnly;")) {
      clientSideCookies.push(cookie);
    } else {
      // For debugging (only when necessary; it can be noisy):
      // console.debug(`Dropped ${cookie.split(";")[0].split("=")[0]} cookie.`);
    }
  });
  return clientSideCookies;
};

export const authenticateWithCredentials = async (
  credentials: Record<string, string>
): Promise<User | null> => {
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
        // eslint-disable-next-line no-console
        // console.log("Response did not contain user data.");
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
      // eslint-disable-next-line no-console
      console.error(`${error}`);
      return Promise.resolve(null);
    });
  return Promise.resolve(user);
};

interface SocialMediaAccountCredentials {
  access_token?: string;
  code?: string;
  token_secret?: string;
  refresh_token?: string;
  user: User;
}

export const authenticateWithSocialMediaAccount = async (
  user: User,
  account: Account
): Promise<User> => {
  const url = makeDjangoApiUrl(`/users/auth/${account.provider}`);
  const credentials: SocialMediaAccountCredentials = { user };
  switch (account.provider) {
    // https://next-auth.js.org/providers/discord
    // https://next-auth.js.org/providers/facebook
    // https://next-auth.js.org/providers/github
    // https://next-auth.js.org/providers/google
    // https://next-auth.js.org/providers/twitter
    case "discord":
    case "facebook":
    case "google":
    case "twitter":
      credentials.access_token = account.accessToken;
      credentials.refresh_token = account.refreshToken;
      break;
    case "github": {
      // https://next-auth.js.org/providers/github
      // Retrieve email address, if necessary.
      if (!user.email) {
        const emailRes = await fetch("https://api.github.com/user/emails", {
          headers: { Authorization: `token ${account.accessToken}` },
        });
        const emails = await emailRes.json();
        if (emails?.length !== 0) {
          user.email = emails.find((emails) => emails.primary).email;
        }
      }
      credentials.access_token = account.accessToken;
      credentials.refresh_token = account.refreshToken;
      break;
    }
    default:
      // eslint-disable-next-line no-console
      console.error("Unsupported provider:", account.provider);
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
    });
  return Promise.resolve(user);
};

// https://next-auth.js.org/tutorials/refresh-token-rotation
export const refreshAccessToken = async (jwt: JWT): Promise<JWT> => {
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
        /*
          Example response:
          {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOzODQzLCJqdGkiOngly0HZdG66ic",
            "access_token_expiration": "2021-03-25T20:24:03.605165Z"
          }
        */
        const accessTokenExpiry = Date.parse(response.data.access_token_expiration);
        const clientSideCookies = removeServerSideCookies(response.headers["set-cookie"]);
        jwt = {
          ...jwt,
          // Fall back to old refresh token if necessary.
          refreshToken: response.data.refresh_token ?? jwt.refreshToken,
          accessToken: response.data.access,
          accessTokenExpiry,
          clientSideCookies,
          iat: Date.now() / 1000,
          exp: accessTokenExpiry / 1000,
        };
        // console.debug("Refreshed access token.");
      } else if (response.data.code === "token_not_valid") {
        // eslint-disable-next-line no-console
        console.debug("Refresh token expired.");
        /*
          Example response:
          {
            "detail": "Token is invalid or expired",
            "code": "token_not_valid"
          }
        */
      } else {
        // eslint-disable-next-line no-console
        console.error(`Failed to parse response: ${response.data}`);
      }
    })
    .catch(function (error) {
      // eslint-disable-next-line no-console
      console.error(`Failed to refresh auth token due to error:\n${error}`);
    });
  return jwt;
};
