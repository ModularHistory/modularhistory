// https://eslint.org/docs/user-guide/configuring/

const sharedRules = {
  "no-console": "off",
  "no-unused-vars": "off",
  "@typescript-eslint/no-unused-vars": [
    "warn",
    { varsIgnorePattern: "^_", ignoreRestSiblings: true },
  ],
  "react/react-in-jsx-scope": ["off"],
  "@typescript-eslint/no-explicit-any": "off",
  "@typescript-eslint/explicit-module-boundary-types": "off",
};

module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  // https://eslint.org/docs/user-guide/configuring/configuration-files#extending-configuration-files
  extends: ["eslint:recommended", "next"],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: "module",
  },
  plugins: ["react"],
  rules: sharedRules,
  // https://eslint.org/docs/user-guide/configuring/configuration-files#how-do-overrides-work
  overrides: [
    {
      files: ["*.ts", "*.tsx", "**/*.ts", "**/*.tsx"],
      extends: [
        "eslint:recommended",
        "plugin:@typescript-eslint/eslint-recommended",
        "plugin:@typescript-eslint/recommended",
        "next",
      ],
      // https://www.npmjs.com/package/@typescript-eslint/parser
      parser: "@typescript-eslint/parser",
      plugins: ["react", "@typescript-eslint"],
      rules: sharedRules,
    },
    {
      files: ["*.test.tsx", "**/*.test.tsx"],
      rules: { "@typescript-eslint/no-non-null-assertion": "off" },
    },
  ],
};
