import { createMcpServer } from '@genkit-ai/mcp';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { isInitializeRequest } from '@modelcontextprotocol/sdk/types.js';
import { randomUUID } from 'node:crypto';
import {
  createServer,
  type IncomingMessage,
  type Server,
  type ServerResponse,
} from 'node:http';
import { pathToFileURL } from 'node:url';

import { env } from '../config/env.js';
import { ai } from '../genkit.js';
import { runWithMcpAuth } from './authContext.js';
import './tools/getAccessiblePatientAppointments.js';
import './tools/getAccessiblePatientClinicalSummary.js';
import './tools/getAccessiblePatientExaminations.js';
import './tools/getAccessiblePatientPrescriptions.js';
import './tools/getAccessibleCTAnalysisResults.js';
import './tools/getBackendStatus.js';
import './tools/getClinicianWorkSummary.js';
import './tools/getMyAppointments.js';
import './tools/getMyMedicationPlan.js';
import './tools/getSystemStatus.js';
import './tools/patientRecordTools.js';
import './tools/searchAccessiblePatients.js';
import './tools/searchAccessibleConsultations.js';
import './tools/searchHospitals.js';

type McpServerInstance = ReturnType<typeof createMcpServer>;

type Session = {
  transport: StreamableHTTPServerTransport;
  mcpServer: McpServerInstance;
  userAccessToken?: string;
};

function headerValue(
  request: IncomingMessage,
  name: string,
): string | undefined {
  const value = request.headers[name];
  return Array.isArray(value) ? value[0] : value;
}

async function readJson(request: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];
  for await (const chunk of request) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  return JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}');
}

function sendJson(
  response: ServerResponse,
  status: number,
  body: unknown,
): void {
  response.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
  });
  response.end(JSON.stringify(body));
}

export async function createMcpHttpServer(
  port = env.mcpServerPort,
  host = env.mcpServerHost,
): Promise<{ server: Server; port: number; close: () => Promise<void> }> {
  const sessions = new Map<string, Session>();

  const server = createServer(async (request, response) => {
    if (!request.url?.startsWith('/mcp')) {
      response.writeHead(404).end();
      return;
    }

    const sessionHeader = request.headers['mcp-session-id'];
    const sessionId = Array.isArray(sessionHeader)
      ? sessionHeader[0]
      : sessionHeader;

    try {
      if (sessionId) {
        const session = sessions.get(sessionId);
        if (!session) {
          sendJson(response, 404, {
            jsonrpc: '2.0',
            error: {
              code: -32001,
              message: 'MCP session not found.',
            },
            id: null,
          });
          return;
        }
        const requestToken = headerValue(request, 'x-brainon-user-token');
        if (
          requestToken
          && session.userAccessToken
          && requestToken !== session.userAccessToken
        ) {
          sendJson(response, 403, {
            jsonrpc: '2.0',
            error: { code: -32003, message: 'MCP session user mismatch.' },
            id: null,
          });
          return;
        }
        await runWithMcpAuth(
          session.userAccessToken,
          () => session.transport.handleRequest(request, response),
        );
        return;
      }

      if (request.method !== 'POST') {
        response.writeHead(405, { Allow: 'POST' }).end('Method Not Allowed');
        return;
      }

      const body = await readJson(request);
      if (!isInitializeRequest(body)) {
        sendJson(response, 400, {
          jsonrpc: '2.0',
          error: {
            code: -32000,
            message: 'MCP initialization request is required.',
          },
          id: null,
        });
        return;
      }

      const mcpServer = createMcpServer(ai, {
        name: 'brainon-mcp',
        version: '0.1.0',
      });
      const userAccessToken = headerValue(
        request,
        'x-brainon-user-token',
      );
      let initializedSessionId: string | undefined;
      const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: randomUUID,
        enableJsonResponse: true,
        onsessioninitialized: (newSessionId) => {
          initializedSessionId = newSessionId;
          sessions.set(newSessionId, {
            transport,
            mcpServer,
            userAccessToken,
          });
        },
      });
      transport.onerror = (error) => {
        console.error('MCP transport error:', error);
      };
      transport.onclose = () => {
        if (initializedSessionId) {
          sessions.delete(initializedSessionId);
        }
      };
      await mcpServer.start(transport);
      await runWithMcpAuth(
        userAccessToken,
        () => transport.handleRequest(request, response, body),
      );
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
      const activeSessions = [...sessions.values()];
      sessions.clear();
      await Promise.all(
        activeSessions.map(async ({ transport, mcpServer }) => {
          await transport.close();
          await mcpServer.server?.close();
        }),
      );
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
