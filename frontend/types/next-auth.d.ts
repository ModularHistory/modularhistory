import "next-auth";
declare module "next-auth" {
  /**
   * Returned by `useSession`, `getSession` and received as a prop on the `Provider` React Context
   */
  interface Session {
    user?: User;
  }
  interface User {
    username: string;
    handle: string;
    avatar: string;
    accessToken: string;
    accessTokenExpiry: number;
    refreshToken: string;
    sessionIdCookie: string;
    clientSideCookies: string[];
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    accessToken: string;
    accessTokenExpiry: number;
    refreshToken: string;
    sessionIdCookie: string;
    clientSideCookies: string[];
  }
}
