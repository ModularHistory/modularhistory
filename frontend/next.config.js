// https://nextjs.org/docs/api-reference/next.config.js/introduction

module.exports = {
  // Delegate static file compression to Nginx in production
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
};
