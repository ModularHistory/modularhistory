// This file sets a custom webpack configuration to use Next.js with Sentry.
// https://nextjs.org/docs/api-reference/next.config.js/introduction
// https://docs.sentry.io/platforms/javascript/guides/nextjs/

// const { withSentryConfig } = require("@sentry/nextjs");
const fs = require("fs");
const readline = require("readline");
const path = require("path");
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

const volumesDir = path.join(process.cwd(), "../_volumes");
const redirectsMapPath = path.join(volumesDir, "redirects/redirects.map");
const redirectRegex = /(.+) (.+);/;

module.exports = {
  // allow tests to be co-located with pages
  pageExtensions: ["page.tsx", "page.ts"],
  swcMinify: true,
  async redirects() {
    const redirects = [];
    if (!fs.existsSync(redirectsMapPath)) {
      console.log(`${redirectsMapPath} does not exist.`);
      await require("axios")
        .get("http://django:8000/api/redirects/")
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
        console.log(redirect);
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
  // images: {
  //   domains: process.env.ENVIRONMENT == "prod" ? [
  //     'modularhistory.com'
  //   ] : [
  //     'modularhistory.dev.net'
  //   ],
  // },
  productionBrowserSourceMaps: true,
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
};
