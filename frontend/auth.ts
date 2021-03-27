import { signOut } from 'next-auth/client';
import axios from './axios';

export const djangoLogoutUrl = '/api/users/auth/logout/';
export const SESSION_TOKEN_COOKIE_NAME = 'next-auth.session-token';

export const handleLogout = (session) => {
  // Sign out of the back end.
  console.log('posting');
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
  document.cookie = `next-auth.callback-url=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
  document.cookie = `${SESSION_TOKEN_COOKIE_NAME}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
  // Sign out of the front end.
  signOut({ callbackUrl: window.location.origin });
};
