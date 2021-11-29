// https://mui.com/guides/minimizing-bundle-size/#development-environment
// https://github.com/umidbekk/babel-plugin-direct-import#nextjs
module.exports = (api) => {
  const target = api.caller((caller) => caller.target);

  api.cache.using(() => JSON.stringify({ target }));

  const presets = ["next/babel"];
  const plugins = [];

  // Enable optimizations only for the `web` bundle.
  if (target === "web") {
    plugins.push([
      "babel-plugin-direct-import",
      { modules: ["@mui/lab", "@mui/material", "@mui/icons-material"] },
    ]);
  }

  return { presets, plugins };
};
