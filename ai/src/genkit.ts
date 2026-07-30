import { googleAI } from '@genkit-ai/google-genai';
import { genkit } from 'genkit/beta';

import { env } from './config/env.js';

export const genkitConfigured = env.geminiApiKey !== null;

export const ai = genkit({
  plugins: genkitConfigured
    ? [googleAI({ apiKey: env.geminiApiKey ?? undefined })]
    : [],
});
