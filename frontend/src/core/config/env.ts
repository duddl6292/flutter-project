export const env = {
  apiBaseUrl:
    import.meta.env.MODE === 'mock'
      ? window.location.origin
      : import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
} as const
