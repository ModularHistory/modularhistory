import {
  authenticateWithCredentials,
  authenticateWithSocialMediaAccount,
  refreshAccessToken,
} from "@/auth";
import axiosWithAuth from "@/axiosWithAuth";
import { NextApiHandler, NextApiRequest, NextApiResponse } from "next";
import NextAuth, {
  Account,
  CallbacksOptions,
  NextAuthOptions,
  PagesOptions,
  Session,
  User,
} from "next-auth";
import { JWT } from "next-auth/jwt";
import Providers from "next-auth/providers";

const makeDjangoApiUrl = (endpoint: string) => {
  return `http://django:8002/api${endpoint}`;
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
  // https://next-auth.js.org/providers/github
  Providers.GitHub({
    clientId: process.env.SOCIAL_AUTH_GITHUB_CLIENT_ID,
    clientSecret: process.env.SOCIAL_AUTH_GITHUB_SECRET,
    scope: "user repo",
  }),
  // https://next-auth.js.org/providers/credentials
  Providers.Credentials({
    id: "credentials",
    name: "Credentials", // name to display on the sign-in form ('Sign in with ____')
    credentials: {
      // fields expected to be submitted in the sign-in form
      username: { label: "Username", type: "text", placeholder: "" },
      password: { label: "Password", type: "password" },
    },
    async authorize(credentials: Record<string, string>) {
      return await authenticateWithCredentials(credentials);
    },
  }),
];

// https://next-auth.js.org/configuration/callbacks
const callbacks: CallbacksOptions = {};

callbacks.signIn = async function signIn(user: User, account: Account) {
  // Respond to the sign-in attempt. If the user signed in with credentials (i.e.,
  // a username and password), authentication with the back-end Django server will
  // have been completed before the signIn callback is reached. However, if the user
  // signed in with a social media account, authentication with the Django server
  // is still required.
  if (account.type != "credentials") {
    user = await authenticateWithSocialMediaAccount(user, account);
  }
  // If there is no error, return true to permit signing in.
  // If there is an error, return false to reject the sign-in attempt.
  return !user.error;
};

// https://next-auth.js.org/configuration/callbacks#jwt-callback
callbacks.jwt = async function jwt(token, user?: User, account?) {
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
    console.log("Refreshing access token...");
    token = await refreshAccessToken(token);
  }
  return Promise.resolve(token);
};

// https://next-auth.js.org/configuration/callbacks#session-callback
callbacks.session = async function session(session: Session, jwt: JWT) {
  if (jwt) {
    // If the access token is expired, ...
    if (Date.now() > jwt.accessTokenExpiry) {
      console.error("Session got an expired access token.");
      jwt = await refreshAccessToken(jwt);
      if (Date.now() > jwt.accessTokenExpiry) {
        // eslint-disable-next-line no-console
        console.log("くそっ！ サインアウトするしかない。");
        session.expired = true;
        return session;
      }
    }
    const accessToken = jwt.accessToken;
    if (jwt.sessionIdCookie) {
      session.sessionIdCookie = jwt.sessionIdCookie;
    }
    if (accessToken) {
      const clientSideCookies = jwt.clientSideCookies;
      session.accessToken = accessToken;
      session.clientSideCookies = clientSideCookies;
      // TODO: Refactor? The point of this is to only make the request when necessary.
      if (!session.user?.["username"]) {
        // Replace the session's `user` attribute (containing only name, image, and
        // a couple other fields) with full user details from the Django API.
        let userData;
        await axiosWithAuth
          .get(makeDjangoApiUrl("/users/me/"), {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          })
          .then((response) => {
            userData = response.data;
          })
          .catch(function (error) {
            if (error.response?.data) {
              console.error(
                "Failed to retrieve user data:",
                error.response.data,
                `${Date.now()} <> ${jwt.accessTokenExpiry}`
              );
            }
          });
        session.user = userData;
      }
    }
  }
  return session;
};

callbacks.redirect = async function redirect(url, baseUrl) {
  url = url.startsWith(baseUrl) ? url : baseUrl;
  // Strip /auth/signin from the redirect URL if necessary, so that the user is
  // not redirected back to the sign-in page after successfully signing in (and
  // is redirected to the homepage instead).
  const path = url.replace(baseUrl, "").replace("/auth/signin", "");
  // Add /auth/redirect to the redirect URL so that the user is first routed to the
  // "redirect page," where Next.js can set or remove cookies before routing the user
  // to the callback URL. Regardless of whether the specified page is served by Django
  // or by Next.js, we have to first hit the redirect page to deal with cookies.
  if (!url.includes("/auth/redirect/")) {
    url = `${baseUrl}/auth/redirect/${path}`;
    // Remove duplicate slashes.
    url = url.replace(/([^:]\/)\/+/g, "$1");
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
