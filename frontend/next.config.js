const dotenv = require('dotenv');

const env = dotenv.config({ path: '../.env' });
if (env.error) {
  throw env.error;
}

// Add 'HOSTNAME' to environment
if (!('HOSTNAME' in env.parsed)) {
  env.parsed['HOSTNAME'] = (
    env.parsed['ENVIRONMENT'] === "dev"
      ? "http://localhost:8000"
      : "https://modularhistory"
  );
} else {
  throw new Error(".env var 'HOSTNAME' is already defined");
}

module.exports = {
  // Delegate static file compression to Nginx in production
  compress: env.parsed['ENVIRONMENT'] === "prod" ? false : true,
  env: env.parsed,
  webpackDevMiddleware: (config) => {
    // Solve compiling problem within Docker
    config.watchOptions = {
      poll: 2000,
      aggregateTimeout: 200,
      ignored: ['.next/', 'node_modules/']
    };
    return config;
  }
};