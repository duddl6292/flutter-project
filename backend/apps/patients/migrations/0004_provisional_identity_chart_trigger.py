from django.db import migrations


FORWARD_SQL = """
CREATE OR REPLACE FUNCTION
patients_audit_provisional_identity_delete()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    resolution_log_id uuid;
BEGIN
    IF OLD.status IS DISTINCT FROM 'RESOLVED'
       OR OLD.resolved_patient_id IS NULL
       OR OLD.resolved_at IS NULL
       OR OLD.resolved_by_id IS NULL THEN
        RAISE EXCEPTION
            '신원확인이 완료되지 않은 임시 신원은 삭제할 수 없습니다.'
            USING ERRCODE = '23514';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM appointments_encounter
        WHERE provisional_identity_id = OLD.id
    ) THEN
        RAISE EXCEPTION
            '연결된 진료 건이 남아 있는 임시 신원은 삭제할 수 없습니다.'
            USING ERRCODE = '23514';
    END IF;

    SELECT id
    INTO resolution_log_id
    FROM patient_identity_resolution_logs
    WHERE provisional_identity_uuid = OLD.id
      AND target_patient_id = OLD.resolved_patient_id
    FOR UPDATE;

    IF resolution_log_id IS NULL THEN
        RAISE EXCEPTION
            '신원확인 처리 로그가 없는 임시 신원은 삭제할 수 없습니다.'
            USING ERRCODE = '23514';
    END IF;

    UPDATE patient_identity_resolution_logs
    SET
        deletion_snapshot = jsonb_build_object(
            'id',
            OLD.id,
            'temporary_number',
            OLD.temporary_number,
            'temporary_name',
            OLD.temporary_name,
            'estimated_sex',
            OLD.estimated_sex,
            'estimated_age',
            OLD.estimated_age,
            'distinguishing_features',
            OLD.distinguishing_features,
            'status',
            OLD.status,
            'resolved_patient_id',
            OLD.resolved_patient_id,
            'resolved_at',
            OLD.resolved_at,
            'resolved_by_id',
            OLD.resolved_by_id,
            'created_at',
            OLD.created_at,
            'updated_at',
            OLD.updated_at,
            'deleted_at',
            CURRENT_TIMESTAMP
        ),
        provisional_deleted_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = resolution_log_id;

    RETURN OLD;
END;
$$;

DROP TRIGGER IF EXISTS
trg_provisional_identity_chart
ON provisional_identities;

CREATE TRIGGER
trg_provisional_identity_chart
BEFORE DELETE ON provisional_identities
FOR EACH ROW
EXECUTE FUNCTION
patients_audit_provisional_identity_delete();
"""


REVERSE_SQL = """
DROP TRIGGER IF EXISTS
trg_provisional_identity_chart
ON provisional_identities;

DROP FUNCTION IF EXISTS
patients_audit_provisional_identity_delete();
"""


class Migration(migrations.Migration):

    dependencies = [
        (
            "patients",
            "0003_patientidentityresolutionlog",
        ),
    ]

    operations = [
        migrations.RunSQL(
            sql=FORWARD_SQL,
            reverse_sql=REVERSE_SQL,
        ),
    ]