import { env } from '../../config/env.js';
import { requireUserAccessToken } from '../authContext.js';

type QueryValue = string | number | boolean | null | undefined;

export async function getBrainOnApi(
  path: string,
  query: Record<string, QueryValue> = {},
): Promise<unknown> {
  const url = new URL(path, `${env.backendInternalUrl}/`);
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, String(value));
    }
  }

  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${requireUserAccessToken()}`,
    },
    signal: AbortSignal.timeout(10_000),
  });
  if (!response.ok) {
    console.warn(
      `[brainon-mcp] backend GET failed: path=${path} status=${response.status}`,
    );
    throw new Error(`BrainOn backend request failed (${response.status}).`);
  }
  return response.json();
}
