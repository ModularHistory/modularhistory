/// <reference types="next" />
/// <reference types="next/types/global" />

import "next-auth";
import { Session as NextAuthSession, User as NextAuthUser } from "next-auth";
import "next-auth/jwt";
import { JWT as NextAuthJWT } from "next-auth/jwt";

declare module "next-auth" {
  export interface Session extends NextAuthSession {
    refreshToken?: string;
    sessionIdCookie?: string;
    clientSideCookies?: Array<str>;
    expired?: boolean;
  }
  export interface User extends NextAuthUser {
    accessToken: string;
    accessTokenExpiry: number;
    refreshToken: string;
    sessionIdCookie: string;
    clientSideCookies: Array<string>;
    error?: string;
  }
}

declare module "next-auth/jwt" {
  export interface JWT extends NextAuthJWT {
    accessToken: string;
    sessionIdCookie: string;
    clientSideCookies: Array<string>;
  }
}
