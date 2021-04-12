/// <reference types="next" />
/// <reference types="next/types/global" />

import "next-auth";
import { Session as NextAuthSession } from "next-auth";

declare module "next-auth" {
  export interface Session extends NextAuthSession {
    refreshToken?: string;
    clientSideCookies?: Array<str>;
  }
}
