import { z } from 'genkit/beta';

import { env } from '../../config/env.js';
import { ai } from '../../genkit.js';

export const backendStatusInputSchema = z.object({});
export const backendStatusOutputSchema = z.object({
  status: z.literal('ok'),
  service: z.literal('brainon-backend'),
  reachable: z.literal(true),
});

export const getBackendStatus = ai.defineTool(
  {
    name: 'getBackendStatus',
    description:
      'Checks whether the BrainOn Django backend is reachable. '
      + 'This tool does not access patients or medical records.',
    inputSchema: backendStatusInputSchema,
    outputSchema: backendStatusOutputSchema,
  },
  async () => {
    const healthUrl = new URL('/api/health/', `${env.backendInternalUrl}/`);
    const response = await fetch(healthUrl, {
      headers: { Accept: 'application/json' },
      signal: AbortSignal.timeout(5_000),
    });

    if (!response.ok) {
      throw new Error(`BrainOn backend health check failed (${response.status}).`);
    }

    const body = (await response.json()) as {
      status?: unknown;
      service?: unknown;
    };
    if (body.status !== 'ok' || body.service !== 'brainon-backend') {
      throw new Error('BrainOn backend returned an unexpected health response.');
    }

    console.info('[brainon-mcp] getBackendStatus executed');
    return {
      status: 'ok' as const,
      service: 'brainon-backend' as const,
      reachable: true as const,
    };
  },
);
