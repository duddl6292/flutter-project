import { vertexAI } from '@genkit-ai/google-genai';
import { z } from 'genkit/beta';

import { env } from '../config/env.js';
import { ai, genkitConfigured } from '../genkit.js';

export const assistantFlow = ai.defineFlow(
  {
    name: 'assistantFlow',
    inputSchema: z.object({
      message: z.string().min(1).max(2000),
    }),
    outputSchema: z.object({
      text: z.string(),
    }),
  },
  async ({ message }) => {
    if (!genkitConfigured) {
      throw new Error('GOOGLE_CLOUD_PROJECT is not configured.');
    }
    const response = await ai.generate({
      model: vertexAI.model(env.aiModel),
      prompt: message,
    });
    return { text: response.text };
  },
);
