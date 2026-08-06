from __future__ import annotations

from datetime import date

from django.db.models import Q
from rest_framework import serializers

from apps.appointments.models import Encounter
from apps.imaging.models import ImagingAsset
from apps.patients.access import (
    accessible_encounters_for_user,
    accessible_patients_for_user,
)
from apps.patients.models import Patient

from .models import CTCase, InferenceJob


class CTAnalysisCreateSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField()
    ct_file = serializers.FileField(required=False)
    imaging_asset_id = serializers.UUIDField(required=False)
    source_case_id = serializers.UUIDField(required=False)
    study_type = serializers.ChoiceField(
        choices=CTCase.StudyType.choices,
        default=CTCase.StudyType.NCCT,
    )
    description = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    encounter_id = serializers.UUIDField(required=False)

    def validate(self, attrs):
        request = self.context["request"]
        try:
            patient = accessible_patients_for_user(
                request.user,
                Patient.objects.all(),
            ).get(id=attrs["patient_id"])
        except Patient.DoesNotExist as exc:
            raise serializers.ValidationError({"patient_id": "환자를 찾을 수 없습니다."}) from exc

        ct_file = attrs.get("ct_file")
        imaging_asset_id = attrs.get("imaging_asset_id")
        source_case_id = attrs.get("source_case_id")
        if sum(bool(value) for value in (ct_file, imaging_asset_id, source_case_id)) != 1:
            raise serializers.ValidationError(
                "기존 CT 영상 또는 업로드할 NIfTI 파일 중 하나를 선택해 주세요."
            )

        encounters = accessible_encounters_for_user(
            request.user,
            Encounter.objects.filter(patient=patient),
        ).select_related("hospital")
        if attrs.get("encounter_id"):
            encounters = encounters.filter(id=attrs["encounter_id"])
        encounter = encounters.order_by("-created_at").first()
        if encounter is None and ct_file:
            raise serializers.ValidationError({
                "patient_id": "이 환자에게 연결할 수 있는 진료 건이 없습니다.",
            })

        imaging_asset = None
        source_case = None
        if imaging_asset_id:
            assets = (
                ImagingAsset.objects
                .filter(
                    id=imaging_asset_id,
                    study__examination__patient=patient,
                    study__modality="CT",
                    asset_type=ImagingAsset.AssetType.NIFTI_VOLUME,
                    stored_object__status="AVAILABLE",
                )
                .select_related("study__examination__hospital", "stored_object")
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
            imaging_asset = assets.first()
            if imaging_asset is None:
                raise serializers.ValidationError({
                    "imaging_asset_id": "선택한 환자의 CT 영상을 찾을 수 없습니다.",
                })

        if source_case_id:
            cases = CTCase.objects.filter(id=source_case_id).filter(
                Q(encounter__patient=patient)
                | Q(imaging_study__examination__patient=patient)
            )
            if request.user.role == "CLINICIAN":
                encounter_ids = accessible_encounters_for_user(
                    request.user
                ).values("id")
                cases = cases.filter(
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
            source_case = cases.first()
            if source_case is None:
                raise serializers.ValidationError({
                    "source_case_id": "선택한 환자의 CT 분석 입력을 찾을 수 없습니다.",
                })

        attrs["patient"] = patient
        attrs["encounter"] = encounter
        attrs["imaging_asset"] = imaging_asset
        attrs["source_case"] = source_case
        return attrs


def _age(birth_date: date | None) -> int | None:
    if birth_date is None:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


class CTCaseSerializer(serializers.BaseSerializer):
    def to_representation(self, case: CTCase):
        jobs = list(case.inference_jobs.all())
        job = jobs[0] if jobs else None
        patient = case.encounter.patient if case.encounter_id else (
            case.imaging_study.examination.patient
            if case.imaging_study_id
            else None
        )
        result = None
        if job is not None:
            try:
                result = job.result
            except InferenceJob.result.RelatedObjectDoesNotExist:
                result = None

        result_data = None
        if result is not None:
            end_to_end_seconds = None
            if job and job.started_at and job.completed_at:
                end_to_end_seconds = max(
                    0.0,
                    (job.completed_at - job.started_at).total_seconds(),
                )
            raw_lesion = (
                result.raw_result.get("result", {})
                if isinstance(result.raw_result, dict)
                else {}
            )
            lesion_slice_indices = raw_lesion.get("lesion_slice_indices", [])
            if not isinstance(lesion_slice_indices, list):
                lesion_slice_indices = []
            result_data = {
                "result_id": str(result.id),
                "model_id": result.model_id,
                "model_version": result.model_version,
                "lesion_detected": result.lesion_voxels > 0,
                "lesion_voxels": result.lesion_voxels,
                "lesion_volume_ml": float(result.lesion_volume_ml or 0),
                "lesion_slice_count": result.lesion_slice_count,
                "lesion_slice_indices": lesion_slice_indices,
                "lesion_slice_start": result.lesion_slice_start,
                "lesion_slice_end": result.lesion_slice_end,
                "max_lesion_slice": result.max_lesion_slice,
                "shape": result.shape,
                "spacing": result.spacing,
                "preprocessing_seconds": float(result.preprocessing_seconds or 0),
                "inference_seconds": float(result.inference_seconds or 0),
                "postprocessing_seconds": float(result.postprocessing_seconds or 0),
                "total_seconds": float(result.total_seconds or 0),
                "end_to_end_seconds": end_to_end_seconds,
                "gpu_memory_peak_mb": (
                    float(result.gpu_memory_peak_mb)
                    if result.gpu_memory_peak_mb is not None
                    else None
                ),
                "source_url": f"/api/v1/ct-analysis/cases/{case.id}/source/",
                "mask_url": f"/api/v1/ct-analysis/cases/{case.id}/mask/",
            }

        return {
            "case_id": str(case.id),
            "display_id": f"CT-{str(case.id).split('-')[0].upper()}",
            "study_type": case.study_type,
            "study_type_label": case.get_study_type_display(),
            "description": case.description,
            "status": case.status,
            "status_label": case.get_status_display(),
            "file_size_bytes": case.file_size_bytes,
            "patient": {
                "patient_id": str(patient.id),
                "medical_record_number": patient.medical_record_number,
                "name": patient.name,
                "sex": patient.sex,
                "age": _age(patient.birth_date),
            } if patient else None,
            "job": {
                "job_id": str(job.id),
                "status": job.status,
                "progress": job.progress,
                "error_code": job.error_code,
                "error_message": job.error_message,
                "error_retryable": job.error_retryable,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
            } if job else None,
            "result": result_data,
            "created_at": case.created_at,
            "updated_at": case.updated_at,
        }
