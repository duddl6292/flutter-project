function parsePort(name: string, fallback: number): number {
  const raw = process.env[name];
  if (!raw) {
    return fallback;
  }
  const value = Number(raw);
  if (!Number.isInteger(value) || value < 1 || value > 65535) {
    throw new Error(`${name} must be an integer between 1 and 65535.`);
  }
  return value;
}

function parseUrl(name: string, fallback: string): string {
  const value = process.env[name] || fallback;
  try {
    return new URL(value).toString().replace(/\/$/, '');
  } catch {
    throw new Error(`${name} must be a valid URL.`);
  }
}

export const env = {
  googleCloudProject:
    process.env.GOOGLE_CLOUD_PROJECT?.trim() ||
    process.env.GCLOUD_PROJECT?.trim() ||
    null,
  googleCloudLocation:
    process.env.GOOGLE_CLOUD_LOCATION?.trim() || 'global',
  aiModel: process.env.AI_MODEL?.trim() || 'gemini-2.5-flash',
  backendInternalUrl: parseUrl(
    'BACKEND_INTERNAL_URL',
    'http://localhost:8000',
  ),
  aiServiceHost: process.env.AI_SERVICE_HOST || '0.0.0.0',
  aiServicePort: parsePort('AI_SERVICE_PORT', 18200),
  mcpServerHost: process.env.MCP_SERVER_HOST || '0.0.0.0',
  mcpServerPort: parsePort('MCP_SERVER_PORT', 18201),
  mcpServerUrl: parseUrl('MCP_SERVER_URL', 'http://localhost:18201'),
} as const;
