from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings

from apps.ct_analysis.adapters import MockInferenceClient, MockStorageService
from apps.notifications.senders import MockNotificationSender


class MockAdapterTests(SimpleTestCase):
    @override_settings(SIGNED_URL_EXPIRES_SECONDS=900)
    def test_mock_storage_issues_scoped_path_and_validates_metadata(self):
        case = SimpleNamespace(id="case-id")
        service = MockStorageService()
        target = service.create_upload_url(case, "application/gzip")
        self.assertEqual(target.object_path, "cases/case-id/input/ct.nii.gz")
        service.verify_upload(
            expected_path=target.object_path, object_path=target.object_path,
            file_size=1, sha256="a" * 64, content_type="application/gzip",
        )

    def test_mock_inference_client_preserves_job_id(self):
        response = MockInferenceClient().create_job({"job_id": "job-id"})
        self.assertEqual(response, {"job_id": "job-id", "status": "QUEUED"})

    def test_mock_notification_sender_does_not_require_firebase(self):
        notification = SimpleNamespace(id="notification-id")
        self.assertEqual(MockNotificationSender().send(notification, [object()]), 1)
