// https://eslint.org/docs/user-guide/configuring/

const rules = {
  "no-console": "warn",
  "no-unused-vars": "off",
  "@typescript-eslint/no-unused-vars": [
    "warn",
    { varsIgnorePattern: "^_", ignoreRestSiblings: true },
  ],
  "react/react-in-jsx-scope": ["off"],
  "@typescript-eslint/no-explicit-any": "warn",
  "@typescript-eslint/explicit-module-boundary-types": "warn",
};

module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  // https://eslint.org/docs/user-guide/configuring/configuration-files#extending-configuration-files
  extends: ["eslint:recommended", "next/core-web-vitals", "plugin:@typescript-eslint/recommended"],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: "module",
  },
  rules,
  // https://eslint.org/docs/user-guide/configuring/configuration-files#how-do-overrides-work
  overrides: [
    {
      files: ["*.test.tsx", "**/*.test.tsx"],
      rules: { "@typescript-eslint/no-non-null-assertion": "off" },
    },
  ],
};
