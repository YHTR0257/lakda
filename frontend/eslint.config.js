import js from "@eslint/js";
import tseslint from "typescript-eslint";
import eslintConfigPrettier from "eslint-config-prettier";

export default [
  { ignores: [".next", "node_modules", "out"] },
  js.configs.recommended,
  tseslint.configs.recommended,
  eslintConfigPrettier,
].flat();
