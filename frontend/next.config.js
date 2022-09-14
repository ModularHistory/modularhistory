// This file sets a custom webpack configuration to use Next.js with Sentry.
// https://nextjs.org/docs/api-reference/next.config.js/introduction
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

const fs = require("fs");
const path = require("path");
const readline = require("readline");
const dotenv = require("dotenv");
const axios = require("axios");
const { withSentryConfig } = require("@sentry/nextjs");

// TODO: set vars based on Dockerization

const DOTENV_DIR = path.join(__dirname, "..");
const DOTENV_PATH = path.join(DOTENV_DIR, ".env");
if (!fs.existsSync(DOTENV_PATH)) {
  throw new Error(`Missing .env file in ${DOTENV_DIR}`);
}
dotenv.config({ path: DOTENV_PATH });

process.env.NEXT_PUBLIC_SENTRY_SERVER_ROOT_DIR = "/app/frontend";
process.env.NEXT_PUBLIC_SENTRY_DSN = process.env.SENTRY_FRONTEND_DSN;
process.env.SENTRY_PROJECT = process.env.SENTRY_FRONTEND_PROJECT;
process.env.SENTRY_RELEASE = `modularhistory@${process.env.VERSION || process.env.SHA || "latest"}`;

if (!process.env.DJANGO_PORT) process.env.DJANGO_PORT = "8000";

const basePath = "";

const sentryWebpackPluginOptions = {
  // Additional config options for the Sentry Webpack plugin. Keep in mind that
  // the following options are set automatically, and overriding them is not
  // recommended:
  //   release, url, org, project, authToken, configFile, stripPrefix,
  //   urlPrefix, include, ignore

  silent: true, // Suppresses all logs
  // For all available options, see:
  // https://github.com/getsentry/sentry-webpack-plugin#options.
};

const volumesDir = path.join(process.cwd(), "../_volumes");
const redirectsMapPath = path.join(volumesDir, "redirects/redirects.map");
const redirectRegex = /(.+) (.+);/;

/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  // allow tests to be co-located with pages
  pageExtensions: ["page.tsx", "page.ts"],
  async redirects() {
    const redirects = [];
    if (!fs.existsSync(redirectsMapPath)) {
      // console.log(`${redirectsMapPath} does not exist.`);
      await axios
        .get(`http://${process.env.DJANGO_HOST}:${process.env.DJANGO_PORT}/api/redirects/`)
        .then(({ data }) => {
          const results = data["results"];
          if (!Array.isArray(results)) {
            for (const redirect of results) {
              redirects.push({
                source: redirect.oldPath,
                destination: redirect.newPath,
                permanent: true,
              });
            }
          }
        })
        .catch(console.error);
    } else {
      const redirectsMapStream = fs.createReadStream(redirectsMapPath);
      const redirectsInterface = readline.createInterface({
        input: redirectsMapStream,
        crlfDelay: Infinity,
      });
      for await (const line of redirectsInterface) {
        const redirect = line.match(redirectRegex);
        redirects.push({
          source: redirect[1],
          destination: redirect[2],
          permanent: true,
        });
      }
    }
    return redirects;
  },
  // Delegate static file compression to Nginx in production.
  // https://nextjs.org/docs/api-reference/next.config.js/compression
  compress: process.env.ENVIRONMENT != "prod",
  env: {
    // Make the version accessible to clients so that Sentry events
    // can be associated with the release they belong to.
    NEXT_PUBLIC_VERSION: process.env.SENTRY_RELEASE,
  },
  experimental: {
    modularizeImports: {
      "react-bootstrap": {
        transform: "react-bootstrap/lib/{{member}}",
      },
      lodash: {
        transform: "lodash/{{member}}",
      },
    },
  },
  sentry: {
    // Use `hidden-source-map` rather than `source-map` as the Webpack `devtool`
    // for client-side builds. (This will be the default starting in
    // `@sentry/nextjs` version 8.0.0.) See
    // https://webpack.js.org/configuration/devtool/ and
    // https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/#use-hidden-source-map
    // for more information.
    hideSourceMaps: true,
  },
};

// Make sure adding Sentry options is the last code to run before exporting, to
// ensure that your source maps include changes from all other Webpack plugins
module.exports = withSentryConfig(nextConfig, sentryWebpackPluginOptions);
