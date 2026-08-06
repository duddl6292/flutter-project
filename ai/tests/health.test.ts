import assert from 'node:assert/strict';
import { once } from 'node:events';
import test from 'node:test';

import { createAiHttpServer } from '../src/http/server.js';

test('health works without a Google Cloud project configuration', async () => {
  const server = createAiHttpServer();
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  const address = server.address();
  assert.ok(address && typeof address === 'object');

  try {
    const response = await fetch(`http://127.0.0.1:${address.port}/health`);
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), {
      status: 'ok',
      service: 'brainon-ai',
      genkit_configured: false,
    });
  } finally {
    server.close();
    await once(server, 'close');
  }
});
