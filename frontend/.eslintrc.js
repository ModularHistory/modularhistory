// https://eslint.org/docs/user-guide/configuring/

const sharedRules = {
  "no-console": "off",
  "no-unused-vars": ["warn", { varsIgnorePattern: "^_" }],
  "@typescript-eslint/no-unused-vars": ["warn", { varsIgnorePattern: "^_" }],
  "react/react-in-jsx-scope": ["off"],
  "@typescript-eslint/no-explicit-any": "off",
  "react-hooks/exhaustive-deps": "off", // TODO: remove this line
  "react-hooks/rules-of-hooks": "off", // TODO: remove this line
  "@typescript-eslint/explicit-module-boundary-types": "off",
};

module.exports = {
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
  ],
};
