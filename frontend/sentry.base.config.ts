import { init } from "@sentry/nextjs";

const SENTRY_DSN = process.env.SENTRY_FRONTEND_DSN || process.env.NEXT_PUBLIC_SENTRY_DSN;
const SENTRY_ENVIRONMENT =
  process.env.SENTRY_ENVIRONMENT ||
  process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT ||
  process.env.NODE_ENV;

type Config = Parameters<typeof init>[0];

export const baseConfig: Config = {
  autoSessionTracking: false,
  debug: process.env.NODE_ENV === "development",
  dsn: SENTRY_DSN || "https://dbdf6f1119f54b8a8058ea9ac1ac3b73@glitchtip.orega.org/2",
  enabled: process.env.NODE_ENV === "production",
  environment: SENTRY_ENVIRONMENT,
  // https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/filtering/#decluttering-sentry
  ignoreErrors: [
    // Random plugins/extensions
    "top.GLOBALS",
    "atomicFindClose",
    // Facebook borked
    "fb_xd_fragment",
  ],
};
