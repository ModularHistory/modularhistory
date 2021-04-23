// This file sets a custom webpack configuration to use Next.js with Sentry.
// https://nextjs.org/docs/api-reference/next.config.js/introduction
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

const { withSentryConfig } = require("@sentry/nextjs");
require("dotenv").config({ path: "../.env" });
const { SENTRY_FRONTEND_DSN, SENTRY_FRONTEND_AUTH_TOKEN, SHA, VERSION } = process.env;

process.env.SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN = SENTRY_FRONTEND_DSN;
process.env.SENTRY_ORG = "modularhistory";
process.env.SENTRY_PROJECT = "frontend";
process.env.SENTRY_AUTH_TOKEN = SENTRY_FRONTEND_AUTH_TOKEN;
process.env.SENTRY_RELEASE = `modularhistory@${VERSION || SHA || "latest"}`;

const moduleExports = {
  // Delegate static file compression to Nginx in production.
  // https://nextjs.org/docs/api-reference/next.config.js/compression
  compress: process.env.ENVIRONMENT != "prod",
  webpackDevMiddleware: (config) => {
    // Solve compiling problem within Docker
    config.watchOptions = {
      poll: 2000,
      aggregateTimeout: 200,
      ignored: [".next/", "node_modules/"],
    };
    return config;
  },
  async redirects() {
    return [
      {
        source: "/occurrences",
        destination: "/search/?content_types=occurrences.occurrence",
        permanent: true,
      },
      {
        source: "/quotes",
        destination: "/search/?content_types=quotes.quote",
        permanent: true,
      },
    ];
  },
};

// The following options are set automatically, and overriding them is not recommended:
// release, url, org, project, authToken, configFile, stripPrefix, urlPrefix, include, ignore
// For all available options, see:
// https://github.com/getsentry/sentry-webpack-plugin#options
const SentryWebpackPluginOptions = {};

// Ensure that adding Sentry options is the last code to run before exporting,
// in order to ensure that source maps include changes from all other Webpack plugins.
module.exports = withSentryConfig(moduleExports, SentryWebpackPluginOptions);
