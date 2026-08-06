from datetime import UTC, datetime
from uuid import UUID

from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clinicians.permissions import IsApprovedClinicianOrAdmin, IsClinicianOrAdmin
from apps.imaging.models import ImagingAsset
from apps.patients.access import (
    accessible_encounters_for_user,
    accessible_patients_for_user,
)
from apps.patients.models import Patient

from .models import CTCase
from .serializers import CTAnalysisCreateSerializer, CTCaseSerializer
from .services import (
    CTAnalysisError,
    create_case_and_job,
    create_retry_job,
    input_from_case,
    input_from_imaging_asset,
    open_gcs_uri,
    run_inference,
    upload_ct_file,
)


def _case_queryset(request):
    queryset = (
        CTCase.objects
        .select_related(
            "encounter__patient",
            "encounter__hospital",
            "imaging_study__examination__patient",
            "imaging_study__examination__hospital",
        )
        .prefetch_related("inference_jobs__result")
    )
    if request.user.role == "CLINICIAN":
        encounter_ids = accessible_encounters_for_user(
            request.user
        ).values("id")
        queryset = queryset.filter(
            Q(encounter_id__in=encounter_ids)
            | Q(
                imaging_study__examination__hospital=(
                    request.user.clinician.hospital
                )
            )
            | Q(
                imaging_study__examination__encounter_id__in=(
                    encounter_ids
                )
            )
        )
    return queryset


class CTCaseListCreateView(APIView):
    permission_classes = [IsClinicianOrAdmin, IsApprovedClinicianOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        try:
            limit = min(max(int(request.query_params.get("limit", "50")), 1), 100)
        except ValueError:
            limit = 50
        cases = _case_queryset(request)
        patient_id = request.query_params.get("patient_id", "").strip()
        if patient_id:
            try:
                parsed_patient_id = UUID(patient_id)
            except ValueError as exc:
                raise ValidationError({
                    "patient_id": "올바른 환자 ID를 입력해 주세요.",
                }) from exc
            cases = cases.filter(
                Q(encounter__patient_id=parsed_patient_id)
                | Q(
                    imaging_study__examination__patient_id=(
                        parsed_patient_id
                    )
                )
            )
        cases = cases[:limit]
        return Response({"data": CTCaseSerializer(cases, many=True).data})

    def post(self, request):
        serializer = CTAnalysisCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data

        try:
            imaging_asset = values.get("imaging_asset")
            source_case = values.get("source_case")
            if source_case is not None:
                uploaded = input_from_case(source_case)
            elif imaging_asset is not None:
                uploaded = input_from_imaging_asset(imaging_asset)
            else:
                uploaded = upload_ct_file(values["ct_file"], values["patient"])
            case, job = create_case_and_job(
                patient=values["patient"],
                encounter=values["encounter"] or (source_case.encounter if source_case else None),
                imaging_asset=imaging_asset,
                source_case=source_case,
                uploaded=uploaded,
                requested_by=request.user,
                study_type=values["study_type"],
                description=values.get("description", ""),
                delete_input_on_failure=(imaging_asset is None and source_case is None),
            )
        except CTAnalysisError as exc:
            response_data = {
                "error": {
                    "code": exc.code,
                    "message": str(exc),
                    "retryable": exc.retryable,
                }
            }
            if "case" in locals():
                refreshed = _case_queryset(request).get(id=case.id)
                response_data["data"] = CTCaseSerializer(refreshed).data
            return Response(response_data, status=status.HTTP_502_BAD_GATEWAY)

        refreshed = _case_queryset(request).get(id=case.id)
        return Response(
            {"data": CTCaseSerializer(refreshed).data},
            status=status.HTTP_201_CREATED,
        )


class CTSourceListView(APIView):
    permission_classes = [IsClinicianOrAdmin, IsApprovedClinicianOrAdmin]

    def get(self, request):
        patient_id = request.query_params.get("patient_id", "").strip()
        if not patient_id:
            return Response({"data": []})
        patient = get_object_or_404(
            accessible_patients_for_user(
                request.user,
                Patient.objects.all(),
            ),
            id=patient_id,
        )
        assets = (
            ImagingAsset.objects
            .filter(
                study__examination__patient=patient,
                study__modality="CT",
                asset_type=ImagingAsset.AssetType.NIFTI_VOLUME,
                stored_object__status="AVAILABLE",
            )
            .select_related("study__examination__hospital", "stored_object")
            .order_by("-study__examination__performed_at", "-created_at")
        )
        if request.user.role == "CLINICIAN":
            encounter_ids = accessible_encounters_for_user(
                request.user
            ).values("id")
            assets = assets.filter(
                Q(
                    study__examination__hospital=(
                        request.user.clinician.hospital
                    )
                )
                | Q(
                    study__examination__encounter_id__in=(
                        encounter_ids
                    )
                )
            )
        data = [
            {
                "source_id": str(asset.id),
                "source_type": "IMAGING_ASSET",
                "imaging_asset_id": str(asset.id),
                "study_id": str(asset.study_id),
                "study_description": asset.study.study_description,
                "performed_at": asset.study.examination.performed_at,
                "filename": asset.stored_object.original_filename,
                "file_size_bytes": asset.stored_object.file_size_bytes,
            }
            for asset in assets[:20]
        ]
        known_uris = {
            f"gs://{asset.stored_object.bucket_name}/{asset.stored_object.object_key}"
            for asset in assets[:20]
        }
        cases = (
            _case_queryset(request)
            .filter(
                Q(encounter__patient=patient)
                | Q(imaging_study__examination__patient=patient)
            )
            .exclude(status=CTCase.Status.ARCHIVED)
            .select_related("encounter__hospital", "imaging_study__examination__hospital")
            .order_by("-performed_at", "-created_at")
        )
        data.extend(
            {
                "source_id": str(case.id),
                "source_type": "CT_CASE",
                "imaging_asset_id": None,
                "study_id": str(case.imaging_study_id) if case.imaging_study_id else None,
                "study_description": case.description or case.get_study_type_display(),
                "performed_at": case.performed_at or case.created_at,
                "filename": case.input_uri.rsplit("/", 1)[-1],
                "file_size_bytes": case.file_size_bytes,
            }
            for case in cases[:20]
            if case.input_uri not in known_uris
        )
        data.sort(
            key=lambda row: row["performed_at"] or datetime.min.replace(tzinfo=UTC),
            reverse=True,
        )
        return Response({"data": data})


class CTCaseRunView(APIView):
    permission_classes = [IsClinicianOrAdmin, IsApprovedClinicianOrAdmin]

    def post(self, request, case_id):
        case = get_object_or_404(_case_queryset(request), id=case_id)
        job = case.inference_jobs.first()
        if job is None:
            return Response(
                {"error": {"code": "JOB_NOT_FOUND", "message": "추론 작업을 찾을 수 없습니다."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        if job.status == job.Status.SUCCEEDED:
            return Response({"data": CTCaseSerializer(case).data})
        if job.status == job.Status.RUNNING:
            return Response(
                {"error": {"code": "JOB_ALREADY_RUNNING", "message": "이미 분석 중입니다."}},
                status=status.HTTP_409_CONFLICT,
            )

        if job.status in {
            job.Status.FAILED,
            job.Status.CANCELLED,
            job.Status.TIMED_OUT,
        }:
            job = create_retry_job(job, requested_by=request.user)

        try:
            run_inference(job)
        except CTAnalysisError as exc:
            refreshed = _case_queryset(request).get(id=case.id)
            return Response(
                {
                    "data": CTCaseSerializer(refreshed).data,
                    "error": {
                        "code": exc.code,
                        "message": str(exc),
                        "retryable": exc.retryable,
                    },
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )
        refreshed = _case_queryset(request).get(id=case.id)
        return Response({"data": CTCaseSerializer(refreshed).data})


class CTCaseDetailView(APIView):
    permission_classes = [IsClinicianOrAdmin, IsApprovedClinicianOrAdmin]

    def get(self, request, case_id):
        case = get_object_or_404(_case_queryset(request), id=case_id)
        return Response({"data": CTCaseSerializer(case).data})


class CTCaseAssetView(APIView):
    permission_classes = [IsClinicianOrAdmin, IsApprovedClinicianOrAdmin]

    def get(self, request, case_id, asset):
        case = get_object_or_404(_case_queryset(request), id=case_id)
        if asset == "source":
            uri = case.input_uri
            filename = "source.nii.gz" if uri.lower().endswith(".nii.gz") else "source.nii"
            content_type = case.content_type
        else:
            job = case.inference_jobs.first()
            if job is None:
                raise Http404
            try:
                result = job.result
                uri = (
                    result.preview_uri
                    if asset == "preview"
                    else result.mask_uri
                )
            except Exception as exc:
                raise Http404 from exc
            if asset == "preview":
                if not uri:
                    raise Http404
                filename = uri.rsplit("/", 1)[-1] or "preview.png"
                content_type = "image/png"
            else:
                filename = "mask.nii.gz"
                content_type = "application/gzip"

        try:
            stream, blob = open_gcs_uri(uri)
        except CTAnalysisError as exc:
            raise Http404(str(exc)) from exc
        response = FileResponse(stream, content_type=content_type, filename=filename)
        if blob.size is not None:
            response["Content-Length"] = str(blob.size)
        response["Cache-Control"] = "private, max-age=300"
        return response
