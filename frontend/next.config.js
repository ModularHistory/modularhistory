// https://nextjs.org/docs/api-reference/next.config.js/introduction

module.exports = {
  // Delegate static file compression to Nginx in production.
  // https://nextjs.org/docs/api-reference/next.config.js/compression
  compress: process.env.ENVIRONMENT === "prod" ? false : true,
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
        source: '/occurrences',
        destination: '/search/?content_types=occurrences.occurrence',
        permanent: true,
      },
      {
        source: '/quotes',
        destination: '/search/?content_types=quotes.quote',
        permanent: true,
      },
    ]
  },
};
