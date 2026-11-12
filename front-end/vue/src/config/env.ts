import { z } from "zod";

const schema = z.object({
  VITE_APP_NAME: z.string().min(1),
  VITE_APP_ENV: z.enum(["development", "testing", "staging", "production"]),
  VITE_API_BASE_URL: z.string().min(1),
});

const parsed = schema.safeParse(import.meta.env);
if (!parsed.success) {
  throw new Error("[Configuration Error] " + parsed.error.issues.map((issue) => issue.message).join("; "));
}

export const appConfig = {
  name: parsed.data.VITE_APP_NAME,
  environment: parsed.data.VITE_APP_ENV,
  apiBaseUrl: parsed.data.VITE_API_BASE_URL,
  apiTimeout: 30_000,
};