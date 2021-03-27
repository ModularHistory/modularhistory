import { Session } from 'next-auth';
import { signIn, signOut } from 'next-auth/client';
import { WithAdditionalParams } from 'next-auth/_utils';
import { Router } from 'next/router';
import axios from './axios';

export const djangoLogoutUrl = '/api/users/auth/logout/';
export const SESSION_TOKEN_COOKIE_NAME = 'next-auth.session-token';

export const handleLogin = (router: Router): void => {
  // If not already on the sign-in page, initiate the sign-in process.
  // (This prevents messing up the callbackUrl by reloading the sign-in page.)
  if (router.pathname != '/auth/signin') {
    signIn();
  }
};

export const handleLogout = (session: WithAdditionalParams<Session>): void => {
  // Sign out of the back end.
  if (session) {
    axios
      .post(
        djangoLogoutUrl,
        { refresh: session.refreshToken },
        {
          headers: {
            Authorization: `Bearer ${session.accessToken}`
          }
        }
      )
      .then(function () {
        console.log('Successfully signed out.');
      })
      .catch(function (error) {
        console.error(`Failed to sign out due to error: ${error}`);
        throw new Error(`${error}`);
      });
  }
  // Remove cookies.
  document.cookie = `next-auth.callback-url=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
  document.cookie = `${SESSION_TOKEN_COOKIE_NAME}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
  // Sign out of the front end.
  signOut({ callbackUrl: window.location.origin });
  // Sign out of other windows.
  // To trigger the event listener, save some random data into the `logout` key.
  window.localStorage.setItem("logout", `${Date.now()}`);
};
