// This config is for initialization of Sentry on the Next.js server.
// It is used whenever the server handles a request (during SSR, etc.).
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from '@sentry/nextjs';

const SENTRY_DSN = process.env.SENTRY_DSN || process.env.NEXT_PUBLIC_SENTRY_DSN;

Sentry.init({
  dsn: SENTRY_DSN || 'https://054ccb00ec274cc292f2472140f8260c@o431037.ingest.sentry.io/5380934',
  // Note: To override the automatic release value, we use the environment variable 
  // `SENTRY_RELEASE`, so that it will also be attached to the source maps.
});
