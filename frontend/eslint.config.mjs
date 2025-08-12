import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals"),
  {
    rules: {
      "@next/next/no-img-element": "off",
      "react/no-unescaped-entities": "off",
      "prefer-const": "warn",
      // API standardization rules - enforce use of ClerkApiService only
      "no-restricted-globals": [
        "error",
        {
          "name": "fetch",
          "message": "Direct fetch usage is not allowed. Use ClerkApiService from '@/services/clerkApi' instead."
        }
      ],
      "no-restricted-imports": [
        "error",
        {
          "paths": [
            {
              "name": "axios",
              "message": "Direct axios usage is not allowed. Use ClerkApiService from '@/services/clerkApi' instead."
            }
          ],
          "patterns": [
            {
              "group": ["*/api.ts", "*/utils/api.ts"],
              "message": "Import API utilities from '@/services/clerkApi' instead to ensure consistent authentication."
            }
          ]
        }
      ]
    },
    languageOptions: {
      globals: {
        React: "readonly"
      }
    }
  },
  // Override for ClerkApiService - allow axios since it's the base implementation
  {
    files: ["**/services/clerkApi.ts"],
    rules: {
      "no-restricted-imports": "off"
    }
  },
];

export default eslintConfig;