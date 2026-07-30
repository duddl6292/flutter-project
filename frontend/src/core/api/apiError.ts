export interface ApiErrorBody {
  error: {
    code: string
    message: string
    details: unknown
  }
}

export class ApiError extends Error {
  constructor(
    readonly code: string,
    message: string,
    readonly status: number,
    readonly details: unknown,
  ) {
    super(message)
    this.name = 'ApiError'
  }

  static async fromResponse(response: Response): Promise<ApiError> {
    try {
      const body = (await response.json()) as Partial<ApiErrorBody>
      const error = body.error
      if (error) {
        return new ApiError(
          error.code,
          error.message,
          response.status,
          error.details,
        )
      }
    } catch {
      // The fallback below intentionally hides non-contract response details.
    }
    return new ApiError(
      'API_ERROR',
      '요청을 처리하지 못했습니다.',
      response.status,
      {},
    )
  }
}
