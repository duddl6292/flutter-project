from django.db import migrations, models


def populate_device_identity(apps, schema_editor):
    Device = apps.get_model(
        "notifications",
        "Device",
    )
    User = apps.get_model(
        "accounts",
        "User",
    )

    for device in Device.objects.all().iterator():
        if device.platform == "WEB":
            client_type = "CLINICIAN_WEB"
        else:
            user_role = (
                User.objects
                .filter(id=device.user_id)
                .values_list("role", flat=True)
                .first()
            )
            client_type = (
                "PATIENT_APP"
                if user_role == "PATIENT"
                else "CLINICIAN_APP"
            )

        device.client_type = client_type
        device.device_identifier = (
            f"legacy-{device.id}"
        )
        device.save(
            update_fields=[
                "client_type",
                "device_identifier",
            ],
        )


class Migration(migrations.Migration):

    dependencies = [
        (
            "notifications",
            (
                "0003_remove_"
                "notificationpreference_"
                "in_app_enabled_and_more"
            ),
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="device",
            name="app_version",
            field=models.CharField(
                blank=True,
                default="",
                max_length=50,
                verbose_name="앱 버전",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="device",
            name="client_type",
            field=models.CharField(
                choices=[
                    (
                        "PATIENT_APP",
                        "환자 앱",
                    ),
                    (
                        "CLINICIAN_APP",
                        "의료진 앱",
                    ),
                    (
                        "CLINICIAN_WEB",
                        "의료진 웹",
                    ),
                ],
                db_index=True,
                max_length=24,
                null=True,
                verbose_name="클라이언트 유형",
            ),
        ),
        migrations.AddField(
            model_name="device",
            name="device_identifier",
            field=models.CharField(
                max_length=255,
                null=True,
                verbose_name=(
                    "앱 설치 또는 브라우저 식별자"
                ),
            ),
        ),
        migrations.RunPython(
            populate_device_identity,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="device",
            name="client_type",
            field=models.CharField(
                choices=[
                    (
                        "PATIENT_APP",
                        "환자 앱",
                    ),
                    (
                        "CLINICIAN_APP",
                        "의료진 앱",
                    ),
                    (
                        "CLINICIAN_WEB",
                        "의료진 웹",
                    ),
                ],
                db_index=True,
                max_length=24,
                verbose_name="클라이언트 유형",
            ),
        ),
        migrations.AlterField(
            model_name="device",
            name="device_identifier",
            field=models.CharField(
                max_length=255,
                verbose_name=(
                    "앱 설치 또는 브라우저 식별자"
                ),
            ),
        ),
        migrations.AddConstraint(
            model_name="device",
            constraint=models.UniqueConstraint(
                fields=(
                    "user",
                    "client_type",
                    "device_identifier",
                ),
                name=(
                    "device_user_client_"
                    "ident_uniq"
                ),
            ),
        ),
        migrations.AddConstraint(
            model_name="device",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(
                        client_type=(
                            "CLINICIAN_WEB"
                        ),
                        platform="WEB",
                    )
                    | models.Q(
                        client_type__in=[
                            "PATIENT_APP",
                            "CLINICIAN_APP",
                        ],
                        platform__in=[
                            "ANDROID",
                            "IOS",
                        ],
                    )
                ),
                name=(
                    "device_client_platform_valid"
                ),
            ),
        ),
    ]
