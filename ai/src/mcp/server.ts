import { createMcpServer } from '@genkit-ai/mcp';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { randomUUID } from 'node:crypto';
import { createServer, type Server } from 'node:http';
import { pathToFileURL } from 'node:url';

import { env } from '../config/env.js';
import { ai } from '../genkit.js';
import './tools/getSystemStatus.js';

export async function createMcpHttpServer(
  port = env.mcpServerPort,
  host = env.mcpServerHost,
): Promise<{ server: Server; port: number; close: () => Promise<void> }> {
  const mcpServer = createMcpServer(ai, {
    name: 'brainon-mcp',
    version: '0.1.0',
  });
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: randomUUID,
    enableJsonResponse: true,
  });
  transport.onerror = (error) => {
    console.error('MCP transport error:', error);
  };
  await mcpServer.start(transport);

  const server = createServer(async (request, response) => {
    if (!request.url?.startsWith('/mcp')) {
      response.writeHead(404).end();
      return;
    }
    try {
      await transport.handleRequest(request, response);
    } catch (error) {
      console.error('MCP request failed:', error);
      if (!response.headersSent) {
        response.writeHead(500, { 'Content-Type': 'application/json' });
      }
      if (!response.writableEnded) {
        response.end(
          JSON.stringify({
            error: {
              code: 'MCP_REQUEST_FAILED',
              message: 'MCP request could not be completed.',
            },
          }),
        );
      }
    }
  });
  await new Promise<void>((resolve, reject) => {
    server.once('error', reject);
    server.listen(port, host, resolve);
  });
  const address = server.address();
  const actualPort =
    typeof address === 'object' && address !== null ? address.port : port;
  return {
    server,
    port: actualPort,
    close: async () => {
      await transport.close();
      await mcpServer.server?.close();
      await new Promise<void>((resolve, reject) => {
        server.close((error) => (error ? reject(error) : resolve()));
      });
    },
  };
}

async function main(): Promise<void> {
  const started = await createMcpHttpServer();
  console.log(`BrainOn MCP listening on ${env.mcpServerHost}:${started.port}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  void main();
}
