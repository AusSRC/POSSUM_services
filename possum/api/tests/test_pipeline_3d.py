import pytest


from django.contrib.auth import get_user_model
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from ..views.pipeline_3d import (
    update_3d_pipeline_val,
    update_3d_val_link,
    update_3d_pipeline,
    tiles_ready_for_ingest    
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
        "api.views.pipeline_3d.update_3d_pipeline_table",
        return_value=1
    )

    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline/?"
                            "band_number=1&"
                            "tile_number=12345&"
                            "3d_pipeline=2025-12-12 00:00:00")
    force_authenticate(request, user=admin_user)
    response = update_3d_pipeline(request)

    mocked.assert_called_once_with(
        tile_number="12345",
        band_number="1",
        status="2025-12-12 00:00:00",
        column_name="3d_pipeline"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('success') == True
    assert response.data.get('rows_updated') == 1

def test_update_3d_pipeline_null(factory, admin_user, mocker):
    """
    Test setting 3d_pipeline to null
    """
    mocked = mocker.patch(
        "api.views.pipeline_3d.update_3d_pipeline_table",
        return_value=1
    )

    request = factory.patch("/api/3d-pipeline/tiles/update/3d_pipeline/?"
                            "band_number=1&"
                            "tile_number=12345")
    force_authenticate(request, user=admin_user)
    response = update_3d_pipeline(request)

    mocked.assert_called_once_with(
        tile_number="12345",
        band_number="1",
        status=None,
        column_name="3d_pipeline"
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