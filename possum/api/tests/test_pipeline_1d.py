import pytest

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from ..views.pipeline_1d import (
    partial_tiles,
    partial_tiles_ready_for_pipeline,
    update_partial_tile_status,
    observations_non_edge_rows,
    boundary_issues,
    full_single_sb_pipeline_table,
    update_single_sb_1d_pipeline
)

User = get_user_model()

@pytest.fixture
def non_staff_user(db):
    return User.objects.create_user(
        username="testuser",
        password="secret"
    )

@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="testuser",
        password="secret",
        is_staff=True
    )


@pytest.fixture
def factory():
    return APIRequestFactory()

#----- Partial tiles tests -----
def test_get_partial_tiles(factory, non_staff_user, mocker):
    """
    Test get partial_tiles
    """
    partial_tiles_rows = [
        {"observation": "EMU_1748-64", "sbid": 54926, 
             "tile1": 11726, "tile2": 11727, "tile3": 11791, "tile4": 11792,
             "type": "corner - crosses projection boundary!"},
        {"observation": "EMU_1748-64", "sbid": 54926, 
             "tile1": 11791, "tile2": 11792, "tile3": 11852, "tile4": 11853,
             "type": "corner - crosses projection boundary!"}
    ]         
    mocked = mocker.patch(
        "api.views.pipeline_1d.get_partial_tiles",
        return_value=partial_tiles_rows
    )

    request = factory.get("/api/1d-pipeline/partial-tiles/band1/")
    force_authenticate(request, user=non_staff_user)
    response = partial_tiles(request, 1)

    mocked.assert_called_once_with(1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == partial_tiles_rows

def test_get_partial_tiles_ready_for_pipeline(factory, non_staff_user, mocker):
    """
    Test get partial_tiles_ready_for_pipeline
    """
    partial_tiles_rows = [
        {"observation": "EMU_1748-64", "sbid": 54926, 
             "tile1": 11726, "tile2": 11727, "tile3": 11791, "tile4": 11792,
             "type": "corner - crosses projection boundary!"},
        {"observation": "EMU_1748-64", "sbid": 54926, 
             "tile1": 11791, "tile2": 11792, "tile3": 11852, "tile4": 11853,
             "type": "corner - crosses projection boundary!"}
    ]         
    mocked = mocker.patch(
        "api.views.pipeline_1d.get_partial_tiles_for_1d_pipeline_run",
        return_value=partial_tiles_rows
    )

    request = factory.get("/api/1d-pipeline/partial-tiles/ready-for-pipeline/band1/")
    force_authenticate(request, user=non_staff_user)
    response = partial_tiles_ready_for_pipeline(request, 1)

    mocked.assert_called_once_with(1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == partial_tiles_rows

def test_update_partial_tile_status_with_tile_numbers(factory, admin_user, mocker):
    """
    Test update_partial_tile_status with tile_numbers provided
    """
    mocked = mocker.patch(
        "api.views.pipeline_1d.update_partial_tile_1d_pipeline_status",
        return_value=1
    )
    request = factory.patch("/api/1d-pipeline/partial-tiles/update/status/",
                           {
                            "band_number": 1,
                            "field_name": "EMU_1748-64",
                            "tile_numbers": ("11726", "11727", "11791", "11792"),
                            "status": "Completed",
                            },
                            format="json")
    force_authenticate(request, user=admin_user)
    response = update_partial_tile_status(request)

    mocked.assert_called_once_with(
        observation="EMU_1748-64",
        tile_numbers=("11726", "11727", "11791", "11792"),
        band_number=1,
        status="Completed"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("rows_updated") == 1

def test_update_partial_tile_status_400(factory, admin_user):
    """
    Test update_partial_tile_status without tile_numbers provided
    """
    request = factory.patch("/api/1d-pipeline/partial-tiles/update/status/",
                           {
                            "band_number": 1,
                            "field_name": "EMU_1748-64",
                            "status": "Completed",
                            },
                            format="json")
    force_authenticate(request, user=admin_user)
    response = update_partial_tile_status(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_update_partial_tile_status_not_admin(factory, non_staff_user):
    """
    Test update_partial_tile_status with non staff admin 
    """
    request = factory.patch("/api/1d-pipeline/partial-tiles/update/status/",
                           {
                            "band_number": 1,
                            "field_name": "EMU_1748-64",
                            "tile_numbers": ("11726", "11727", "11791", "11792"),
                            "status": "Completed",
                            },
                            format="json")
    force_authenticate(request, user=non_staff_user)
    response = update_partial_tile_status(request)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_boundary_issues(factory, non_staff_user, mocker):
    """
    Test get boundary_issues
    """
    mocked = mocker.patch(
        "api.views.pipeline_1d.find_boundary_issues",
        return_value=True
    )

    request = factory.get("/api/1d-pipeline/partial-tiles/boundary-issues")
    force_authenticate(request, user=non_staff_user)
    response = boundary_issues(request, 1, "EMU-12345")

    mocked.assert_called_once_with("EMU-12345", 1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == True        

# #----- Observation_state_band1 table tests -----    

def test_get_observations_non_edge_rows(factory, non_staff_user, mocker):
    """
    Test get observations_non_edge_rows
    """
    non_edge_rows = [
        {"observation": "EMU_1748-64", "sbid": 54926 },
        {"observation": "EMU_1748-65", "sbid": 54925}
    ]         
    mocked = mocker.patch(
        "api.views.pipeline_1d.get_observations_non_edge_rows",
        return_value=non_edge_rows
    )

    request = factory.get("/api/1d-pipeline/observations/non-edge-rows/band1/")
    force_authenticate(request, user=non_staff_user)
    response = observations_non_edge_rows(request, 1)

    mocked.assert_called_once_with(1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == non_edge_rows    

def test_get_full_single_sb_pipeline_table(factory, non_staff_user, mocker):
    """
    Test get full_single_sb_pipeline_table
    """
    rows = [
        {"observation": "EMU_1748-64", "sbid": 54926 },
        {"observation": "EMU_1748-65", "sbid": 54925}
    ]         
    mocked = mocker.patch(
        "api.views.pipeline_1d.get_full_table_single_SB_pipeline",
        return_value=rows
    )

    request = factory.get("/api/1d-pipeline/observations/full_single_sb_pipeline_table/band1/")
    force_authenticate(request, user=non_staff_user)
    response = full_single_sb_pipeline_table(request, 1)

    mocked.assert_called_once_with(1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == rows 

def test_update_partial_tile_status_with_tile_numbers(factory, admin_user, mocker):
    """
    Test update_partial_tile_status with tile_numbers provided
    """
    mocked = mocker.patch(
        "api.views.pipeline_1d.update_partial_tile_1d_pipeline_status",
        return_value=1
    )
    request = factory.patch("/api/1d-pipeline/partial-tiles/update/status/",
                           {
                            "band_number": 1,
                            "field_name": "EMU_1748-64",
                            "tile_numbers": ("11726", "11727", "11791", "11792"),
                            "status": "Completed",
                            },
                            format="json")
    force_authenticate(request, user=admin_user)
    response = update_partial_tile_status(request)

    mocked.assert_called_once_with(
        observation="EMU_1748-64",
        tile_numbers=("11726", "11727", "11791", "11792"),
        band_number=1,
        status="Completed"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("rows_updated") == 1
    
def test_update_single_sb_1d_pipeline(factory, admin_user, mocker):
    """
    Test update_single_sb_1d_pipeline with value
    """
    mocked = mocker.patch(
        "api.views.pipeline_1d.update_1d_pipeline_table",
        return_value=1
    )
    request = factory.patch("/api/1d-pipeline/observations/update/single_sb_1d_pipeline/?"
                            "band_number=1&"
                            "field_name=EMU_1748-64&"
                            "status=Completed")
    force_authenticate(request, user=admin_user)
    response = update_single_sb_1d_pipeline(request)

    mocked.assert_called_once_with(
        field_name="EMU_1748-64",
        band_number="1",
        status="Completed",
        column_name='single_sb_1d_pipeline'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("rows_updated") == 1

def test_update_single_sb_1d_pipeline_null(factory, admin_user, mocker):
    """
    Test update_single_sb_1d_pipeline to NULL
    """
    mocked = mocker.patch(
        "api.views.pipeline_1d.update_1d_pipeline_table",
        return_value=1
    )
    request = factory.patch("/api/1d-pipeline/observations/update/single_sb_1d_pipeline/?"
                            "band_number=1&"
                            "field_name=EMU_1748-64")
    force_authenticate(request, user=admin_user)
    response = update_single_sb_1d_pipeline(request)

    mocked.assert_called_once_with(
        field_name="EMU_1748-64",
        band_number="1",
        status=None,
        column_name='single_sb_1d_pipeline'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("rows_updated") == 1    

def test_update_single_sb_1d_pipeline_non_admin(factory, non_staff_user):
    """
    Test update_single_sb_1d_pipeline with non admin user
    """
    request = factory.patch("/api/1d-pipeline/observations/update/single_sb_1d_pipeline/?"
                            "band_number=1&"
                            "field_name=EMU_1748-64&"
                            "status=Completed")
    force_authenticate(request, user=non_staff_user)
    response = update_single_sb_1d_pipeline(request)
    assert response.status_code == status.HTTP_403_FORBIDDEN
