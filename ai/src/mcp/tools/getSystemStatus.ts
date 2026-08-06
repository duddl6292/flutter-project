import { z } from 'genkit/beta';

import { ai } from '../../genkit.js';

export const systemStatusInputSchema = z.object({});
export const systemStatusOutputSchema = z.object({
  status: z.literal('ok'),
  service: z.literal('brainon-mcp'),
  database_access: z.literal(false),
});

export const getSystemStatus = ai.defineTool(
  {
    name: 'getSystemStatus',
    description: 'Returns non-medical BrainOn MCP service status.',
    inputSchema: systemStatusInputSchema,
    outputSchema: systemStatusOutputSchema,
  },
  async () => {
    console.info('[brainon-mcp] getSystemStatus executed');
    return {
      status: 'ok' as const,
      service: 'brainon-mcp' as const,
      database_access: false as const,
    };
  },
);
