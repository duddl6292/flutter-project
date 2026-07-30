import { googleAI } from '@genkit-ai/google-genai';
import { z } from 'genkit/beta';

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
      throw new Error('GEMINI_API_KEY is not configured.');
    }
    const response = await ai.generate({
      model: googleAI.model('gemini-2.5-flash'),
      prompt: message,
    });
    return { text: response.text };
  },
);
