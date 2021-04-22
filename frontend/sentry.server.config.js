// This file configures the initialization of Sentry on the server.
// The config you add here will be used whenever the server handles a request.
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

import * as Sentry from '@sentry/nextjs';

const SENTRY_DSN = process.env.SENTRY_DSN || process.env.SENTRY_FRONTEND_DSN;

Sentry.init({
  dsn: SENTRY_DSN || 'https://054ccb00ec274cc292f2472140f8260c@o431037.ingest.sentry.io/5380934',
  // Note: To override the automatic release value, we use the environment variable 
  // `SENTRY_RELEASE`, so that it will also be attached to the source maps.
});
