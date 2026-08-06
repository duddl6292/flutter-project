import { createMcpClient } from '@genkit-ai/mcp';

import { env } from '../config/env.js';

export function createBrainOnMcpClient(
  userAccessToken?: string,
  url = `${env.mcpServerUrl}/mcp`,
) {
  return createMcpClient({
    name: 'brainonMcp',
    mcpServer: {
      url,
      requestInit: userAccessToken
        ? { headers: { 'X-BrainOn-User-Token': userAccessToken } }
        : undefined,
    },
  });
}
