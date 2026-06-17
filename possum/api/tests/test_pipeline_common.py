# tests/api/test_pipeline_common_views.py

import pytest

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from ..views.pipeline_common import (
    tiles,
    tiles_observations,
    observations,
)

User = get_user_model()

@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="testuser",
        password="secret"
    )


@pytest.fixture
def factory():
    return APIRequestFactory()


# ----------------------------------------------------------------------
# tiles
# ----------------------------------------------------------------------

def test_tiles_success(factory, test_user, mocker):
    expected_rows = [
        {"tile": 5184, "ra_deg": 0, "dec_deg": 8.386, "gl": 101.797, "gb": -52.363},
        {"tile": 5185, "ra_deg": 2.812, "dec_deg": 8.386, "gl": 106.196, "gb": -53.175},
    ]

    mocker.patch(
        "api.views.pipeline_common.get_all_tiles",
        return_value=expected_rows,
    )

    request = factory.get("/api/common/tiles/")
    force_authenticate(request, user=test_user)
    response = tiles(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_rows


def test_tiles_exception(factory, test_user, mocker):
    mocker.patch(
        "api.views.pipeline_common.get_all_tiles",
        side_effect=Exception("Database error"),
    )

    request = factory.get("/api/common/tiles/")
    force_authenticate(request, user=test_user)
    response = tiles(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "Database error"}


# ----------------------------------------------------------------------
# tiles_observations
# ----------------------------------------------------------------------

def test_tiles_observations_success(factory, test_user, mocker):
    expected_rows = [
        {"tile": 5229, "obs": "EMU_0835+04B,EMU_0835+04A", "n_obs": 2, "n_complete": 2, "3d_pipeline_val": "Running"},
        {"tile": 5230, "obs": "EMU_0835+04B,EMU_0835+04A", "n_obs": 2, "n_complete": 2, "3d_pipeline_val": "WaitingForValidation"}
    ]

    mocked = mocker.patch(
        "api.views.pipeline_common.get_tiles_and_observations",
        return_value=expected_rows,
    )

    request = factory.get("/api/common/tiles-observations/1/")
    force_authenticate(request, user=test_user)
    response = tiles_observations(request, 1)

    mocked.assert_called_once_with(1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_rows


def test_tiles_observations_exception(factory, test_user):
    request = factory.get("/api/common/tiles-observations//")
    force_authenticate(request, user=test_user)
    response = tiles_observations(request, 3)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "band_number must be either 1 or 2"}


# ----------------------------------------------------------------------
# observations
# ----------------------------------------------------------------------

def test_observations_success(factory, test_user, mocker):
    expected_rows = [
        {"name": "EMU_0734-72", "ra_deg": 113.70165, "dec_deg": -72.32725806},
        {"name": "EMU_0733-84", "ra_deg": 113.4551417, "dec_deg": -84.11695306}
    ]

    mocked = mocker.patch(
        "api.views.pipeline_common.get_observations",
        return_value=expected_rows,
    )

    request = factory.get("/api/common/observations/1/")
    force_authenticate(request, user=test_user)
    response = observations(request, 1)

    mocked.assert_called_once_with(1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_rows


def test_observations_exception(factory, test_user, mocker):
    mocker.patch(
        "api.views.pipeline_common.get_observations",
        side_effect=Exception("Database error"),
    )

    request = factory.get("/api/common/observations/1/")
    force_authenticate(request, user=test_user)
    response = observations(request, 1)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "Database error"}