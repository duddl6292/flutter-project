import { AsyncLocalStorage } from 'node:async_hooks';

type McpAuthContext = {
  userAccessToken?: string;
};

const authStorage = new AsyncLocalStorage<McpAuthContext>();

export function runWithMcpAuth<T>(
  userAccessToken: string | undefined,
  callback: () => T,
): T {
  return authStorage.run({ userAccessToken }, callback);
}

export function requireUserAccessToken(): string {
  const token = authStorage.getStore()?.userAccessToken;
  if (!token) {
    throw new Error('Authenticated BrainOn user context is required.');
  }
  return token;
}
