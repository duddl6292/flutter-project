import assert from 'node:assert/strict';
import test from 'node:test';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';

import { createMcpHttpServer } from '../src/mcp/server.js';
import {
  systemStatusInputSchema,
  systemStatusOutputSchema,
} from '../src/mcp/tools/getSystemStatus.js';

test('mock tool schemas accept only the documented status shape', () => {
  assert.deepEqual(systemStatusInputSchema.parse({}), {});
  assert.deepEqual(
    systemStatusOutputSchema.parse({
      status: 'ok',
      service: 'brainon-mcp',
      database_access: false,
    }),
    {
      status: 'ok',
      service: 'brainon-mcp',
      database_access: false,
    },
  );
});

test('MCP client can discover the non-medical status tool', async () => {
  const started = await createMcpHttpServer(0, '127.0.0.1');
  const client = new Client(
    { name: 'brainon-mcp-test', version: '0.1.0' },
  );
  try {
    await client.connect(
      new StreamableHTTPClientTransport(
        new URL(`http://127.0.0.1:${started.port}/mcp`),
      ),
    );
    const tools = await client.listTools();
    assert.ok(
      tools.tools.some((tool) => tool.name === 'getSystemStatus'),
    );
  } finally {
    await client.close();
    await started.close();
  }
});
