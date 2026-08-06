import { createServer, type IncomingMessage, type ServerResponse } from 'node:http';
import { pathToFileURL } from 'node:url';

import { env } from '../config/env.js';
import { assistantFlow } from '../flows/assistantFlow.js';
import { genkitConfigured } from '../genkit.js';

function sendJson(
  response: ServerResponse,
  status: number,
  body: unknown,
): void {
  response.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  response.end(JSON.stringify(body));
}

async function readJson(request: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];
  for await (const chunk of request) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  return JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}');
}

export function createAiHttpServer() {
  return createServer(async (request, response) => {
    if (request.method === 'GET' && request.url === '/health') {
      sendJson(response, 200, {
        status: 'ok',
        service: 'brainon-ai',
        genkit_configured: genkitConfigured,
      });
      return;
    }
    if (request.method === 'POST' && request.url === '/assistant') {
      if (!genkitConfigured) {
        sendJson(response, 503, {
          error: {
            code: 'AI_NOT_CONFIGURED',
            message: 'GOOGLE_CLOUD_PROJECT is not configured.',
            details: {},
          },
        });
        return;
      }
      try {
        const input = (await readJson(request)) as { message?: unknown };
        if (typeof input.message !== 'string' || input.message.length === 0) {
          sendJson(response, 400, {
            error: {
              code: 'VALIDATION_ERROR',
              message: 'message is required.',
              details: {},
            },
          });
          return;
        }
        const userTokenHeader = request.headers['x-brainon-user-token'];
        const userAccessToken = Array.isArray(userTokenHeader)
          ? userTokenHeader[0]
          : userTokenHeader;
        const userRoleHeader = request.headers['x-brainon-user-role'];
        const userRole = Array.isArray(userRoleHeader)
          ? userRoleHeader[0]
          : userRoleHeader;
        sendJson(response, 200, await assistantFlow({
          message: input.message,
          userAccessToken,
          userRole: (
            userRole === 'PATIENT'
            || userRole === 'CLINICIAN'
            || userRole === 'ADMIN'
          ) ? userRole : undefined,
        }));
      } catch (error) {
        console.error(
          '[brainon-ai] assistant request failed:',
          error instanceof Error ? error.stack ?? error.message : error,
        );
        sendJson(response, 500, {
          error: {
            code: 'AI_REQUEST_FAILED',
            message: 'AI request could not be completed.',
            details: {},
          },
        });
      }
      return;
    }
    sendJson(response, 404, {
      error: { code: 'NOT_FOUND', message: 'Not found.', details: {} },
    });
  });
}

async function main(): Promise<void> {
  const server = createAiHttpServer();
  server.listen(env.aiServicePort, env.aiServiceHost, () => {
    console.log(
      `BrainOn AI listening on ${env.aiServiceHost}:${env.aiServicePort}`,
    );
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  void main();
}
