# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-21 12:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

CURRENT_EMR_RELEASES = ("5.2.1", "5.0.0")


def create_emr_releases(apps, schema_editor):
    EMRRelease = apps.get_model("clusters", "EMRRelease")

    for current_release in CURRENT_EMR_RELEASES:

        EMRRelease.objects.get_or_create(
            version=current_release,
            changelog_url="https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-%s/emr-release-components.html"
            % current_release,
        )


def remove_emr_releases(apps, schema_editor):
    EMRRelease = apps.get_model("clusters", "EMRRelease")
    EMRRelease.objects.filter(version__in=CURRENT_EMR_RELEASES).delete()


class Migration(migrations.Migration):

    dependencies = [("clusters", "0019_auto_20170314_1216")]

    operations = [
        migrations.CreateModel(
            name="EMRRelease",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.CharField(max_length=50, primary_key=True, serialize=False),
                ),
                (
                    "changelog_url",
                    models.TextField(
                        default="",
                        help_text="The URL of the changelog with details about the release.",
                    ),
                ),
                (
                    "help_text",
                    models.TextField(
                        default="",
                        help_text="Optional help text to show for users when creating a cluster.",
                    ),
                ),
                (
                    "is_experimental",
                    models.BooleanField(
                        default=False,
                        help_text="Whether this version should be shown to users as experimental.",
                    ),
                ),
                (
                    "is_deprecated",
                    models.BooleanField(
                        default=False,
                        help_text="Whether this version should be shown to users as deprecated.",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "EMR releases",
                "get_latest_by": "created_at",
                "verbose_name": "EMR release",
                "ordering": ["-version"],
            },
        ),
        migrations.RunPython(create_emr_releases, remove_emr_releases),
    ]
