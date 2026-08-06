import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Raised when the internal Genkit service cannot answer a request."""


def request_assistant_reply(
    *,
    message: str,
    user_access_token: str | None = None,
    user_role: str | None = None,
) -> str:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }
    if user_access_token:
        headers["X-BrainOn-User-Token"] = user_access_token
    if user_role:
        headers["X-BrainOn-User-Role"] = user_role

    request = Request(
        f"{settings.AI_SERVICE_URL}/assistant",
        data=json.dumps(
            {"message": message},
            ensure_ascii=False,
        ).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urlopen(
            request,
            timeout=settings.AI_SERVICE_TIMEOUT_SECONDS,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        status_code = exc.code if isinstance(exc, HTTPError) else None
        logger.exception(
            "BrainOn AI request failed (error_type=%s, status=%s)",
            type(exc).__name__,
            status_code,
        )
        raise AIServiceError(
            "AI 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요."
        ) from exc

    text = payload.get("text") if isinstance(payload, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise AIServiceError(
            "AI 서비스가 올바른 답변을 반환하지 않았습니다."
        )
    return text.strip()
