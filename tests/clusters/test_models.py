# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
from datetime import timedelta

import pytest
from django.utils import timezone

from atmo.clusters import models
from atmo.stats.models import Metric


@pytest.mark.parametrize(
    # first is a regular pytest param, all other are pytest-factoryboy params
    ",".join(
        [
            "queryset_method",
            "emr_release__is_experimental",
            "emr_release__is_deprecated",
            "emr_release__is_active",
        ]
    ),
    [
        ["stable", False, False, True],
        ["experimental", True, False, True],
        ["deprecated", False, True, True],
    ],
)
def test_emr_release_querysets(
    queryset_method,
    emr_release__is_active,
    emr_release__is_deprecated,
    emr_release__is_experimental,
    emr_release,
):
    assert getattr(models.EMRRelease.objects, queryset_method)().exists()


@pytest.mark.parametrize(
    # first is a regular pytest param, second is a pytest-factoryboy param
    "queryset_method,cluster__most_recent_status",
    [
        ["active", models.Cluster.STATUS_STARTING],
        ["active", models.Cluster.STATUS_BOOTSTRAPPING],
        ["active", models.Cluster.STATUS_RUNNING],
        ["active", models.Cluster.STATUS_WAITING],
        ["active", models.Cluster.STATUS_TERMINATING],
        ["terminated", models.Cluster.STATUS_TERMINATED],
        ["failed", models.Cluster.STATUS_TERMINATED_WITH_ERRORS],
    ],
)
def test_cluster_querysets(queryset_method, cluster__most_recent_status, cluster):
    assert getattr(models.Cluster.objects, queryset_method)().exists()


def test_is_expiring_soon(cluster):
    assert not cluster.is_expiring_soon
    # the cut-off is at 1 hour
    cluster.expires_at = timezone.now() + timedelta(minutes=59)
    cluster.save()
    assert cluster.is_expiring_soon


def test_extend(client, user, cluster_factory):
    cluster = cluster_factory(
        most_recent_status=models.Cluster.STATUS_WAITING, created_by=user
    )

    assert cluster.lifetime_extension_count == 0
    # expires_at auto-set by save() by cluster.lifetime
    assert cluster.expires_at is not None
    original_expires_at = cluster.expires_at

    cluster.extend(hours=3)
    cluster.refresh_from_db()
    assert cluster.lifetime_extension_count == 1
    assert cluster.expires_at > original_expires_at
    assert cluster.expires_at == original_expires_at + timedelta(hours=3)

    metric = Metric.objects.get(key="cluster-extension")
    assert metric.value == 1
    assert metric.data == {
        "identifier": cluster.identifier,
        "size": cluster.size,
        "jobflow_id": cluster.jobflow_id,
    }


def test_metric_records_emr_version(cluster_provisioner_mocks, cluster_factory):
    cluster = cluster_factory()
    cluster.id = None
    cluster.jobflow_id = None
    cluster.save()

    assert Metric.objects.get(key="cluster-emr-version").data == {
        "version": str(cluster.emr_release.version)
    }


def test_natural_sorting(emr_release_factory):
    # create EMR releases out of order to force PKs to be not consecutive
    third = emr_release_factory(version="5.9.0")
    second = emr_release_factory(version="5.8.0")
    first = emr_release_factory(version="5.2.1")
    fourth = emr_release_factory(version="5.11.0")

    expected = [fourth.version, third.version, second.version, first.version]

    versions = models.EMRRelease.objects.all().values_list("version", flat=True)

    assert list(versions) != expected

    versions = models.EMRRelease.objects.natural_sort_by_version().values_list(
        "version", flat=True
    )
    assert versions.ordered
    assert list(versions) == expected
