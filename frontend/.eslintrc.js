// https://eslint.org/docs/user-guide/configuring/
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  // https://eslint.org/docs/user-guide/configuring/configuration-files#extending-configuration-files
  extends: ['eslint:recommended', 'plugin:react/recommended'],
  parserOptions: {
    ecmaFeatures: {
      jsx: true
    },
    ecmaVersion: 12,
    sourceType: 'module'
  },
  plugins: ['react'],
  rules: {
    'no-unused-vars': ['warn', { varsIgnorePattern: '^_' }],
    '@typescript-eslint/no-unused-vars': ['warn', { varsIgnorePattern: '^_' }]
  },
  // https://eslint.org/docs/user-guide/configuring/configuration-files#how-do-overrides-work
  overrides: [
    {
      files: ['*.ts', '*.tsx', '**/*.ts', '**/*.tsx'],
      extends: [
        'eslint:recommended',
        'plugin:react/recommended',
        'plugin:@typescript-eslint/eslint-recommended',
        'plugin:@typescript-eslint/recommended'
      ],
      // https://www.npmjs.com/package/@typescript-eslint/parser
      parser: '@typescript-eslint/parser',
      plugins: ['react', '@typescript-eslint']
    }
  ]
};
