import pytest

from django.contrib.auth import get_user_model
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from ..views.pipeline_1d import (
    partial_tiles,
    partial_tiles_ready_for_pipeline,
    partial_tiles_by_observation_name,
    update_partial_tile_status,
    new_partial_tiles,
    observations_non_edge_rows,
    observations_complete_partial_tiles,
    boundary_issues,
    full_single_sb_pipeline_table,
    update_single_sb_1d_pipeline,
    update_1d_pipeline_validation
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

#----- Get Partial tiles tests -----
def test_partial_tiles_resolve():
    match = resolve("/api/1d-pipeline/partial-tiles/band1/")
    assert match.func == partial_tiles
    assert match.kwargs == {"band_number": 1}

def test_get_partial_tiles_success(factory, non_staff_user, mocker):
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

def test_get_partial_tiles_ready_for_pipeline_resolve():
    match = resolve("/api/1d-pipeline/partial-tiles/ready-for-pipeline/band1/")
    assert match.func == partial_tiles_ready_for_pipeline
    assert match.kwargs == {"band_number": 1}

def test_get_partial_tiles_ready_for_pipeline_success(factory, non_staff_user, mocker):
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

def test_get_complete_partial_tiles_resolve():
    match = resolve("/api/1d-pipeline/partial-tiles/complete-partial-tiles/band1/")
    assert match.func == observations_complete_partial_tiles
    assert match.kwargs == {"band_number": 1}    

def test_get_complete_partial_tiles_success(factory, non_staff_user, mocker):
    """
    Test get observations_complete_partial_tiles
    """
    partial_tiles_rows = [
        {"observation": "EMU_1748-64", "sbid": 54926, "all_complete": True},
        {"observation": "EMU_1748-65", "sbid": 54925, "all_complete": False}
    ]         
    mocked = mocker.patch(
        "api.views.pipeline_1d.get_observations_with_complete_partial_tiles",
        return_value=partial_tiles_rows
    )

    request = factory.get("/api/1d-pipeline/partial-tiles/complete-partial-tiles/band1/")
    force_authenticate(request, user=non_staff_user)
    response = observations_complete_partial_tiles(request, 1)

    mocked.assert_called_once_with(1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == partial_tiles_rows

def test_get_partial_tiles_by_observation_name_resolve():
    match = resolve("/api/1d-pipeline/partial-tiles/skip-boundary-issues/band1/EMU_1748-64/")
    assert match.func == partial_tiles_by_observation_name
    assert match.kwargs == {"band_number": 1, "field_name": "EMU_1748-64"}

def test_get_partial_tiles_by_observation_name_success(factory, non_staff_user, mocker):
    """
    Test get partial_tiles_by_observation_name
    """
    partial_tiles_rows = [
        {"1d_pipeline": "completed", "tile1": 11315, "tile2": None, "tile3": None, "tile4": None},
        {"1d_pipeline": "completed", "tile1": 11316, "tile2": None, "tile3": None, "tile4": None}
    ]
    mocked = mocker.patch(
        "api.views.pipeline_1d.get_partial_tiles_by_observation",
        return_value=partial_tiles_rows
    )
    request = factory.get("/api/1d-pipeline/partial-tiles/skip-boundary-issues/band1/EMU_1748-65/?skip_boundary_issues=true")
    force_authenticate(request, user=non_staff_user)
    response = partial_tiles_by_observation_name(request, 1, "EMU_12345")

    mocked.assert_called_once_with(1, "EMU_12345", True)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == partial_tiles_rows

#----- Update Partial tiles tests ------

def test_update_partial_tile_1d_pipeline_status_resolve():
    match = resolve("/api/1d-pipeline/partial-tiles/update/status/")
    assert match.func == update_partial_tile_status

def test_update_partial_tile_status_with_tile_numbers_success(factory, admin_user, mocker):
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
                            "tile_numbers": ["11726", "11727", "11791", "11792"],
                            "status": "Completed",
                            },
                            format="json")
    force_authenticate(request, user=admin_user)
    response = update_partial_tile_status(request)

    mocked.assert_called_once_with(
        field_name="EMU_1748-64",
        tile_numbers=("11726", "11727", "11791", "11792"),
        band_number=1,
        status="Completed"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("rows_updated") == 1

def test_update_partial_tile_status_500(factory, admin_user):
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
    print('RESPONSE',response)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data.get("error") == "{'tile_numbers': [ErrorDetail(string='This field is required.', code='required')]}"

def test_update_partial_tile_status_not_admin(factory, non_staff_user):
    """
    Test update_partial_tile_status with non staff admin 
    """
    request = factory.patch("/api/1d-pipeline/partial-tiles/update/status/",
                           {
                            "band_number": 1,
                            "field_name": "EMU_1748-64",
                            "tile_numbers": ["11726", "11727", "11791", "11792"],
                            "status": "Completed",
                            },
                            format="json")
    force_authenticate(request, user=non_staff_user)
    response = update_partial_tile_status(request)
    assert response.status_code == status.HTTP_403_FORBIDDEN

#----- Get Boundary Issues tests ------

def test_boundary_issues_resolve():
    match = resolve("/api/1d-pipeline/partial-tiles/boundary-issues/band1/EMU-12345/")
    assert match.func == boundary_issues
    assert match.kwargs == {"band_number": 1, "observation": "EMU-12345"}

def test_get_boundary_issues_success(factory, non_staff_user, mocker):
    """
    Test get boundary_issues
    """
    mocked = mocker.patch(
        "api.views.pipeline_1d.find_boundary_issues",
        return_value=True
    )

    request = factory.get("/api/1d-pipeline/partial-tiles/boundary-issues/band1/EMU-12345/")
    force_authenticate(request, user=non_staff_user)
    response = boundary_issues(request, 1, "EMU-12345")

    mocked.assert_called_once_with("EMU-12345", 1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == True

#----- Insert Partial Tiles tests -----

def test_new_partial_tiles_resolve():
    match = resolve("/api/1d-pipeline/partial-tiles/new/band1/")
    assert match.func == new_partial_tiles
    assert match.kwargs == {"band_number": 1}

def test_new_partial_tiles_non_admin(factory, non_staff_user):
    """
    Test new_partial_tiles with non staff admin
    """
    request = factory.post("/api/1d-pipeline/partial-tiles/new/band1/?"
                            "field_name=EMU_1748-64&"
                            "tile1=11726&"
                            "tile2=11727&"
                            "tile3=11791&"
                            "tile4=11792&"
                            "type=corner%20-%20crosses projection boundary!&"
                            "num_sources=2"
    )
    force_authenticate(request, user=non_staff_user)
    response = new_partial_tiles(request, 1)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_new_partial_tiles_success(factory, admin_user, mocker):
    """
    Test new_partial_tiles
    """
    mocked = mocker.patch(
        "api.views.pipeline_1d.insert_partial_tiles",
        return_value=1
    )
    request = factory.post("/api/1d-pipeline/partial-tiles/new/band1/?"
                            "field_name=EMU_1748-64&"
                            "tile1=11726&"
                            "tile2=11727&"
                            "tile3=11791&"
                            "tile4=11792&"
                            "type=corner%20-%20crosses projection boundary!&"
                            "num_sources=2"
    )
    force_authenticate(request, user=admin_user)
    response = new_partial_tiles(request, 1)
    mocked.assert_called_once_with(
        field_name="EMU_1748-64",
        tile1="11726",
        tile2="11727",
        tile3="11791",
        tile4="11792",
        type="corner - crosses projection boundary!",
        num_sources="2",
        band_number=1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("rows_inserted") == 1

#----- Get Observation_state_band1 table tests -----    

def test_get_observations_non_edge_rows_resolve():
    match = resolve("/api/1d-pipeline/observations/non-edge-rows/band1/")
    assert match.func == observations_non_edge_rows
    assert match.kwargs == {"band_number": 1}

def test_get_observations_non_edge_rows_success(factory, non_staff_user, mocker):
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

def test_get_full_single_sb_pipeline_table_resolve():
    match = resolve("/api/1d-pipeline/observations/single-sb-1d-pipeline/full-table/band1/")
    assert match.func == full_single_sb_pipeline_table
    assert match.kwargs == {"band_number": 1}

def test_get_full_single_sb_pipeline_table_success(factory, non_staff_user, mocker):
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

    request = factory.get("/api/1d-pipeline/observations/single-sb-1d-pipeline/full-table/band1/")
    force_authenticate(request, user=non_staff_user)
    response = full_single_sb_pipeline_table(request, 1)

    mocked.assert_called_once_with(1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == rows 

#----- Update observations table tests -----

def test_update_1d_pipeline_validation_resolve():
    match = resolve("/api/1d-pipeline/observations/update/1d-pipeline-validation/")
    assert match.func == update_1d_pipeline_validation

def test_update_1d_pipeline_validation_success(factory, admin_user, mocker):
    """
    Test update_1d_pipeline_validation with value
    """
    mocked = mocker.patch(
        "api.views.pipeline_1d.update_1d_pipeline_table",
        return_value=1
    )
    
    request = factory.patch("/api/1d-pipeline/observations/update/1d-pipeline-validation/?"
                            "band_number=1&"
                            "field_name=EMU_1748-64&"
                            "status=Completed")
    force_authenticate(request, user=admin_user)
    response = update_1d_pipeline_validation(request)

    mocked.assert_called_once_with(
        field_name="EMU_1748-64",
        band_number="1",
        status="Completed",
        column_name='1d_pipeline_validation'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("rows_updated") == 1

def test_update_single_sb_1d_pipeline_resolve():
    match = resolve("/api/1d-pipeline/observations/update/single-sb-1d-pipeline/")
    assert match.func == update_single_sb_1d_pipeline

def test_update_single_sb_1d_pipeline_success(factory, admin_user, mocker):
    """
    Test update_single_sb_1d_pipeline with value
    """
    mocked = mocker.patch(
        "api.views.pipeline_1d.update_1d_pipeline_table",
        return_value=1
    )
    request = factory.patch("/api/1d-pipeline/observations/update/single-sb-1d-pipeline/?"
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
    request = factory.patch("/api/1d-pipeline/observations/update/single-sb-1d-pipeline/?"
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
    request = factory.patch("/api/1d-pipeline/observations/update/single-sb-1d-pipeline/?"
                            "band_number=1&"
                            "field_name=EMU_1748-64&"
                            "status=Completed")
    force_authenticate(request, user=non_staff_user)
    response = update_single_sb_1d_pipeline(request)
    assert response.status_code == status.HTTP_403_FORBIDDEN

