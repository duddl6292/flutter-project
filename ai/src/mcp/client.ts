import { createMcpClient } from '@genkit-ai/mcp';

import { env } from '../config/env.js';

export function createBrainOnMcpClient(url = `${env.mcpServerUrl}/mcp`) {
  return createMcpClient({
    name: 'brainonMcp',
    mcpServer: { url },
  });
}
