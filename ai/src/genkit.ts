import { vertexAI } from '@genkit-ai/google-genai';
import { genkit } from 'genkit/beta';

import { env } from './config/env.js';

export const genkitConfigured = env.googleCloudProject !== null;

export const ai = genkit({
  plugins: genkitConfigured
    ? [
        vertexAI({
          projectId: env.googleCloudProject ?? undefined,
          location: env.googleCloudLocation,
        }),
      ]
    : [],
});
