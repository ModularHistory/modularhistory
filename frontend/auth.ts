import { Session } from "next-auth";
import { signIn, signOut } from "next-auth/client";
import { Router } from "next/router";
import axios from "./axiosWithAuth";

export const DJANGO_CSRF_COOKIE_NAME = "csrftoken";
export const DJANGO_LOGOUT_URL = "/api/users/auth/logout/";
export const LOGIN_PAGE_PATH = "/auth/signin";
export const AUTH_REDIRECT_PATH = "/auth/redirect";
export const NEXT_AUTH_CSRF_COOKIE_NAME = "next-auth.csrf-token";
export const AUTH_COOKIES = [
  "next-auth.session-token",
  "next-auth.callback-url",
  "access-token",
  "refresh-token",
  "sessionid",
];

export interface Credentials {
  username: string;
  password: string;
}

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
        console.log("Signed out.");
      })
      .catch(function (error) {
        console.error(`Failed to sign out due to error: ${error}`);
      });
  }
  // Remove cookies by setting their expiry to a past date.
  AUTH_COOKIES.forEach((cookieName) => {
    document.cookie = `${cookieName}; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
  });
  // Sign out of the front end.
  signOut({ callbackUrl: window.location.origin });
  // TODO: Save random data to the `logout` key in local storage
  // to trigger the event listener to sign out of any other open windows.
  window.localStorage.setItem("logout", `${Date.now()}`);
};

export const removeServerSideCookies = (cookies: Array<string>): Array<string> => {
  // Given an array of cookie strings, remove any HttpOnly cookies.
  // Return the modified array.
  const clientSideCookies = [];
  cookies.forEach((cookie) => {
    if (!cookie.includes("HttpOnly;")) {
      clientSideCookies.push(cookie);
    } else {
      console.log(`Dropped ${cookie.split(";")[0].split("=")[0]} cookie.`);
    }
  });
  return clientSideCookies;
};
