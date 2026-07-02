import datetime
import zoneinfo

import pytest


from django.contrib.auth import get_user_model
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from ..views.pipeline_3d import (
    update_3d_pipeline_val,
    update_3d_val_link,
    update_3d_pipeline,
    update_3d_pipeline_ingest,
    tiles_ready_for_ingest,
    tiles_ready_for_3dpipeline,
    tiles_for_3d_plotting,
    tiles_for_tile_id
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

#----- update_3d_pipeline_val tests -----
def test_update_3d_pipeline_val_resolve():
    match = resolve("/api/3d-pipeline/tiles/update/3d_pipeline_val/")
    assert match.func == update_3d_pipeline_val

def test_update_3d_pipeline_val_with_non_admin_user(factory, non_staff_user):
    """
    Updates should fail for non staff user
    """
    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline_val/?band_number=1"
                            "&tile_number=12345"
                            "&3d_pipeline_val=Completed")
    
    force_authenticate(request, user=non_staff_user)
    response = update_3d_pipeline_val(request)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_update_3d_pipeline_val_null(factory, admin_user, mocker):
    """
    Test setting 3d_pipeline_val to null
    """
    mocked = mocker.patch(
        "api.views.pipeline_3d.update_3d_pipeline_table",
        return_value=1
    )

    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline_val/?band_number=1"
                            "&tile_number=12345")
    force_authenticate(request, user=admin_user)
    response = update_3d_pipeline_val(request)

    mocked.assert_called_once_with(
        tile_number="12345",
        band_number="1",
        status=None,
        column_name="3d_pipeline_val"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('success') == True
    assert response.data.get('rows_updated') == 1

def test_update_3d_pipeline_val(factory, admin_user, mocker):
    """
    Test setting 3d_pipeline_val to a value
    """
    mocker.patch(
        "api.views.pipeline_3d.update_3d_pipeline_table",
        return_value=1
    )

    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline_val/?"
                            "band_number=1&"
                            "tile_number=12345&"
                            "3d_pipeline_val=Completed")
    force_authenticate(request, user=admin_user)
    response = update_3d_pipeline_val(request)

    mocker.assert_called_once_with(
        tile_number="12345",
        band_number="1",
        status="Completed",
        column_name="3d_pipeline_val"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('success') == True
    assert response.data.get('rows_updated') == 1

def test_update_3d_pipeline_val(factory, admin_user, mocker):
    """
    Test setting 3d_pipeline_val to a value
    """
    mocked = mocker.patch(
        "api.views.pipeline_3d.update_3d_pipeline_table",
        return_value=1
    )

    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline_val/?"
                            "band_number=1&"
                            "tile_number=12345&"
                            "3d_pipeline_val=Completed")
    force_authenticate(request, user=admin_user)
    response = update_3d_pipeline_val(request)

    mocked.assert_called_once_with(
        tile_number="12345",
        band_number="1",
        status="Completed",
        column_name="3d_pipeline_val"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('success') == True
    assert response.data.get('rows_updated') == 1

#----- update_3d_pipeline_ingest tests -----

def test_update_3d_pipeline_ingest_resolve():
    match = resolve("/api/3d-pipeline/tiles/update/3d_pipeline_ingest/")
    assert match.func == update_3d_pipeline_ingest

def test_update_3d_pipeline_ingest_with_non_admin_user(factory, non_staff_user):
    """
    Updates should fail for non staff user
    """
    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline_ingest/?band_number=1"
                            "&tile_number=12345"
                            "&3d_pipeline_ingest=Completed")
    
    force_authenticate(request, user=non_staff_user)
    response = update_3d_pipeline_ingest(request)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_update_3d_pipeline_ingest_null(factory, admin_user, mocker):
    """
    Test setting 3d_pipeline_ingest to null
    """
    mocked = mocker.patch(
        "api.views.pipeline_3d.update_3d_pipeline_table",
        return_value=1
    )

    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline_ingest/?band_number=1"
                            "&tile_number=12345")
    force_authenticate(request, user=admin_user)
    response = update_3d_pipeline_ingest(request)

    mocked.assert_called_once_with(
        tile_number="12345",
        band_number="1",
        status=None,
        column_name="3d_pipeline_ingest"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('success') == True
    assert response.data.get('rows_updated') == 1

def test_update_3d_pipeline_ingest(factory, admin_user, mocker):
    """
    Test setting 3d_pipeline_ingest to a value
    """
    mocker.patch(
        "api.views.pipeline_3d.update_3d_pipeline_table",
        return_value=1
    )

    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline_ingest/?"
                            "band_number=1&"
                            "tile_number=12345&"
                            "3d_pipeline_ingest=Completed")
    force_authenticate(request, user=admin_user)
    response = update_3d_pipeline_ingest(request)

    mocker.assert_called_once_with(
        tile_number="12345",
        band_number="1",
        status="Completed",
        column_name="3d_pipeline_ingest"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('success') == True
    assert response.data.get('rows_updated') == 1

def test_update_3d_pipeline_ingest(factory, admin_user, mocker):
    """
    Test setting 3d_pipeline_ingest to a value
    """
    mocked = mocker.patch(
        "api.views.pipeline_3d.update_3d_pipeline_table",
        return_value=1
    )

    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline_ingest/?"
                            "band_number=1&"
                            "tile_number=12345&"
                            "3d_pipeline_ingest=Completed")
    force_authenticate(request, user=admin_user)
    response = update_3d_pipeline_ingest(request)

    mocked.assert_called_once_with(
        tile_number="12345",
        band_number="1",
        status="Completed",
        column_name="3d_pipeline_ingest"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('success') == True
    assert response.data.get('rows_updated') == 1    

#----- update_3d_val_link tests -----
def test_update_3d_val_link_resolve():
    match = resolve("/api/3d-pipeline/tiles/update/3d_val_link/")
    assert match.func == update_3d_val_link

def test_update_3d_val_link(factory, admin_user, mocker):
    """
    Test setting 3d_val_link to a value
    """
    mocked = mocker.patch(
        "api.views.pipeline_3d.update_3d_pipeline_table",
        return_value=1
    )

    request = factory.patch("/api/3d-pipeline/tiles/update/3d_val_link/?"
                            "band_number=1&"
                            "tile_number=12345&"
                            "3d_val_link=RandomLink")
    force_authenticate(request, user=admin_user)
    response = update_3d_val_link(request)

    mocked.assert_called_once_with(
        tile_number="12345",
        band_number="1",
        status="RandomLink",
        column_name="3d_val_link"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('success') == True
    assert response.data.get('rows_updated') == 1

def test_update_3d_val_link_null(factory, admin_user, mocker):
    """
    Test setting 3d_val_link to null
    """
    mocked = mocker.patch(
        "api.views.pipeline_3d.update_3d_pipeline_table",
        return_value=1
    )

    request = factory.patch("/api/3d-pipeline/tiles/update/3d_val_link/?"
                            "band_number=1&"
                            "tile_number=12345&")
    force_authenticate(request, user=admin_user)
    response = update_3d_val_link(request)

    mocked.assert_called_once_with(
        tile_number="12345",
        band_number="1",
        status=None,
        column_name="3d_val_link"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('success') == True
    assert response.data.get('rows_updated') == 1

def test_update_3d_val_link_with_non_admin_user(factory, non_staff_user):
    """
    Test setting 3d_val_link with non staff user should be denied
    """
    request = factory.patch("/api/3d-pipeline/tiles/update/3d_val_link/?"
                            "band_number=1&"
                            "tile_number=12345&"
                            "3d_val_link=RandomLink")
    force_authenticate(request, user=non_staff_user)
    response = update_3d_val_link(request)

    assert response.status_code == status.HTTP_403_FORBIDDEN

#----- update_3d_pipeline tests -----
def test_update_3d_pipeline_resolve():
    match = resolve("/api/3d-pipeline/tiles/update/3d_pipeline/")
    assert match.func == update_3d_pipeline

def test_update_3d_pipeline(factory, admin_user, mocker):
    """
    Test setting 3d_pipeline to a value
    """
    mocked = mocker.patch(
        "api.views.pipeline_3d.update_3d_pipeline_timestamp",
        return_value=1
    )

    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline/",
                            {
                             "band_number":1,
                             "tile_number":12345,
                             "timestamp":"2025-12-12 00:00:00"
                            },
                            format="json")
    force_authenticate(request, user=admin_user)
    response = update_3d_pipeline(request)

    mocked.assert_called_once_with(
        tile_number=12345,
        band_number=1,
        timestamp= datetime.datetime(2025, 12, 12, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('success') == True
    assert response.data.get('rows_updated') == 1

def test_update_3d_pipeline_null(factory, admin_user, mocker):
    """
    Test setting 3d_pipeline to null
    """
    mocked = mocker.patch(
        "api.views.pipeline_3d.update_3d_pipeline_timestamp",
        return_value=1
    )

    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline/",
                            {
                            "band_number": 1,
                            "tile_number": 12345,
                            "timestamp": None
                            }, format="json")
    force_authenticate(request, user=admin_user)
    response = update_3d_pipeline(request)

    mocked.assert_called_once_with(
        tile_number=12345,
        band_number=1,
        timestamp=None
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('success') == True
    assert response.data.get('rows_updated') == 1

def test_update_3d_pipeline_with_non_admin_user(factory, non_staff_user):
    """
    Test setting 3d_pipeline with a non staff user
    """
    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline/?"
                            "band_number=1&"
                            "tile_number=12345&"
                            "3d_pipeline=2025-12-12 00:00:00")
    force_authenticate(request, user=non_staff_user)
    response = update_3d_pipeline(request)

    assert response.status_code == status.HTTP_403_FORBIDDEN

#----- tiles_ready_for_ingest tests -----
def test_tiles_ready_for_ingest_resolve():
    match = resolve("/api/3d-pipeline/tiles/ready-for-ingest/band1/")
    assert match.func == tiles_ready_for_ingest
    assert match.kwargs == {"band_number": 1}

def test_tiles_ready_for_ingest(factory, non_staff_user, mocker):
    expected_tiles=[
            {"tile": 5184},
            {"tile": 5185}
    ]
    mocked = mocker.patch(
        "api.views.pipeline_3d.get_tiles_for_ingest",
        return_value=expected_tiles
    )

    request = factory.get("/api/3d-pipeline/tiles/ready-for-ingest/band1/")
    force_authenticate(request, user=non_staff_user)
    response = tiles_ready_for_ingest(request, 1)

    mocked.assert_called_once_with(1) 
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_tiles

#----- Tiles_ready_for_3d tests -----

def test_tiles_ready_for_3d_resolve():
    match = resolve("/api/3d-pipeline/tiles/ready-for-3d/band1/")
    assert match.func == tiles_ready_for_3dpipeline
    assert match.kwargs == {"band_number": 1}

def test_tiles_ready_for_3d(factory, non_staff_user, mocker):
    expected_tiles=[
            {"tile": 5184},
            {"tile": 5185}
    ]
    mocked = mocker.patch(
        "api.views.pipeline_3d.get_tiles_for_pipeline_run",
        return_value=expected_tiles
    )

    request = factory.get("/api/3d-pipeline/tiles/ready-for-3d/band1/")
    force_authenticate(request, user=non_staff_user)
    response = tiles_ready_for_3dpipeline(request, 1)

    mocked.assert_called_once_with(1) 
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_tiles

#----- Tiles_for_tile_id tests -----

def test_tiles_for_tile_id_resolve():
    match = resolve("/api/3d-pipeline/tiles/tile-id/band1/12345/")
    assert match.func == tiles_for_tile_id
    assert match.kwargs == {"band_number": 1, "tile_id": "12345"}

def test_tiles_for_tile_id(factory, non_staff_user, mocker):
    expected_tiles=[
            {"tile": "12345"}
    ]
    mocked = mocker.patch(
        "api.views.pipeline_3d.get_tiles_with_filter",
        return_value=expected_tiles
    )

    request = factory.get("/api/3d-pipeline/tiles/tile-id/band1/12345/")
    force_authenticate(request, user=non_staff_user)
    response = tiles_for_tile_id(request, 1, "12345")

    mocked.assert_called_once_with(1, 
                                   column_name = 'tile',
                                   column_value = '12345',
                                   order_by_3d_pipeline_ingest = False)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_tiles

#----- Tiles_for_3d_plotting tests -----

def test_tiles_for_3d_plotting_resolve():
    match = resolve("/api/3d-pipeline/tiles/plotting/band1/")
    assert match.func == tiles_for_3d_plotting
    assert match.kwargs == {"band_number": 1}

def test_tiles_for_3d_plotting(factory, non_staff_user, mocker):
    expected_tiles=[
            {"tile": 5184},
            {"tile": 5185}
    ]
    mocked = mocker.patch(
        "api.views.pipeline_3d.get_tiles_for_3d_plot",
        return_value=expected_tiles
    )

    request = factory.get("/api/3d-pipeline/tiles/plotting/band1/")
    force_authenticate(request, user=non_staff_user)
    response = tiles_for_3d_plotting(request, 1)

    mocked.assert_called_once_with(1) 
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected_tiles
