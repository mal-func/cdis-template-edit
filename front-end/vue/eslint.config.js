import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import vue from "eslint-plugin-vue";

export default tseslint.config(
  { ignores: ["dist/**", "coverage/**"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...vue.configs["flat/recommended"],
  {
    files: ["**/*.vue"],
    languageOptions: {
      parserOptions: { parser: tseslint.parser }
    }
  },
  {
    files: ["**/*.{ts,vue}"],
    rules: {
      // TypeScript's compiler resolves symbols and types; ESLint's core
      // no-undef rule does not understand type-only references in SFC scripts.
      "no-undef": "off"
    }
  },
  {
    files: ["**/*.{js,ts,vue}"],
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
    rules: {
      "@typescript-eslint/no-explicit-any": "warn",
      "vue/multi-word-component-names": "off"
    }
  }
);