import logging
from dataclasses import dataclass

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class InferenceClientError(RuntimeError):
    pass


class HttpInferenceClient:
    def _client(self):
        return httpx.Client(
            base_url=settings.INFERENCE_BASE_URL,
            headers={"X-Internal-API-Key": settings.INFERENCE_INTERNAL_API_KEY},
            timeout=httpx.Timeout(
                connect=settings.INFERENCE_CONNECT_TIMEOUT_SECONDS,
                read=settings.INFERENCE_READ_TIMEOUT_SECONDS,
                write=30,
                pool=5,
            ),
        )

    def create_job(self, payload):
        try:
            with self._client() as client:
                response = client.post("/internal/v1/inference/jobs", json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            raise InferenceClientError("Inference gateway request failed") from exc

    def get_job(self, job_id):
        try:
            with self._client() as client:
                response = client.get(f"/internal/v1/inference/jobs/{job_id}")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            raise InferenceClientError("Inference gateway request failed") from exc


class MockInferenceClient:
    def create_job(self, payload):
        return {"job_id": str(payload["job_id"]), "status": "QUEUED"}

    def get_job(self, job_id):
        return {"job_id": str(job_id), "status": "QUEUED", "progress": 0}


def get_inference_client():
    return MockInferenceClient() if settings.INFERENCE_USE_MOCK else HttpInferenceClient()


@dataclass
class UploadTarget:
    upload_url: str
    object_path: str
    expires_in: int


class MockStorageService:
    def create_upload_url(self, case, content_type):
        object_path = f"cases/{case.id}/input/ct.nii.gz"
        return UploadTarget(
            upload_url=f"mock://upload/{object_path}",
            object_path=object_path,
            expires_in=settings.SIGNED_URL_EXPIRES_SECONDS,
        )

    def verify_upload(self, *, expected_path, object_path, file_size, sha256, content_type):
        logger.info("mock_storage_verification", extra={"object_path": object_path})
        if object_path != expected_path:
            raise ValueError("Object path does not match the issued upload target.")
        if file_size <= 0 or len(sha256) != 64 or not content_type:
            raise ValueError("Invalid upload metadata.")


class GoogleCloudStorageService:
    def __init__(self):
        from google.cloud import storage
        self.client = storage.Client()

    def create_upload_url(self, case, content_type):
        bucket = self.client.bucket(settings.GCS_BUCKET_MEDICAL_DATA)
        object_path = f"cases/{case.id}/input/ct.nii.gz"
        blob = bucket.blob(object_path)
        url = blob.generate_signed_url(
            version="v4", expiration=settings.SIGNED_URL_EXPIRES_SECONDS,
            method="PUT", content_type=content_type,
        )
        return UploadTarget(url, object_path, settings.SIGNED_URL_EXPIRES_SECONDS)

    def verify_upload(self, *, expected_path, object_path, file_size, sha256, content_type):
        if object_path != expected_path:
            raise ValueError("Object path does not match the issued upload target.")
        blob = self.client.bucket(settings.GCS_BUCKET_MEDICAL_DATA).blob(object_path)
        blob.reload()
        if blob.size != file_size or blob.content_type != content_type:
            raise ValueError("Uploaded object metadata does not match.")


def get_storage_service():
    if settings.STORAGE_BACKEND == "gcs":
        return GoogleCloudStorageService()
    return MockStorageService()
