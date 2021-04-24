// This file sets a custom webpack configuration to use Next.js with Sentry.
// https://nextjs.org/docs/api-reference/next.config.js/introduction
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

// const { withSentryConfig } = require("@sentry/nextjs");
const SentryWebpackPlugin = require("@sentry/webpack-plugin");
require("dotenv").config({ path: "../.env" });
const { SENTRY_FRONTEND_DSN, SHA, VERSION } = process.env;

process.env.NEXT_PUBLIC_SENTRY_SERVER_ROOT_DIR = "/modularhistory/frontend";
process.env.NEXT_PUBLIC_SENTRY_DSN = SENTRY_FRONTEND_DSN;
process.env.SENTRY_ORG = "modularhistory";
process.env.SENTRY_PROJECT = "frontend";
process.env.SENTRY_RELEASE = `modularhistory@${VERSION || SHA || "latest"}`;

const basePath = "";

// Build and upload source maps to Sentry only in production
// and only if all necessary env variables are configured.
const uploadSourceMaps =
  process.env.ENVIRONMENT === "prod" &&
  process.env.SENTRY_DSN &&
  process.env.SENTRY_ORG &&
  process.env.SENTRY_PROJECT &&
  process.env.SENTRY_AUTH_TOKEN &&
  process.env.SHA;

module.exports = {
  // Delegate static file compression to Nginx in production.
  // https://nextjs.org/docs/api-reference/next.config.js/compression
  compress: process.env.ENVIRONMENT != "prod",
  productionBrowserSourceMaps: true,
  env: {
    // Make the version accessible to clients so that Sentry events
    // can be associated with the release they belong to.
    NEXT_PUBLIC_VERSION: process.env.SENTRY_RELEASE,
  },
  webpack: (config, options) => {
    if (!options.isServer) {
      config.resolve.alias["@sentry/node"] = "@sentry/browser";
    }
    config.plugins.push(
      new options.webpack.DefinePlugin({
        "process.env.NEXT_IS_SERVER": JSON.stringify(options.isServer.toString()),
      })
    );
    if (uploadSourceMaps) {
      config.plugins.push(
        new SentryWebpackPlugin({
          include: ".next",
          ignore: ["node_modules"],
          stripPrefix: ["webpack://_N_E/"],
          urlPrefix: `~${basePath}/_next`,
          release: process.env.SENTRY_RELEASE,
        })
      );
    }
    return config;
  },
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
