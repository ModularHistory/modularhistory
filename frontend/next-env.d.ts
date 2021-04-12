/// <reference types="next" />
/// <reference types="next/types/global" />

import "next-auth";
import { JWT as NextAuthJWT, Session as NextAuthSession, User as NextAuthUser } from "next-auth";

declare module "next-auth" {
  export interface Session extends NextAuthSession {
    refreshToken?: string;
    clientSideCookies?: Array<str>;
  }
  export interface JWT extends NextAuthJWT {
    accessToken: string;
    clientSideCookies: Array<string>;
  }
  export interface User extends NextAuthUser {
    accessToken: string;
    refreshToken: string;
    clientSideCookies: Array<string>;
    error?: string;
  }
}
