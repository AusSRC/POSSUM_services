from django.urls import path

from .views import (
    TilesReadyForIngestAPI,
    TilesReadyFor3DPipelineAPI,
    Update1DPipelineAPI,
    Update3DPipelineAPI,
)

urlpatterns = [
    path(
        "tiles/band/<int:band_number>/ready-ingest/",
        TilesReadyForIngestAPI.as_view(),
    ),

    path(
        "tiles/band/<int:band_number>/ready-3d/",
        TilesReadyFor3DPipelineAPI.as_view(),
    ),

    path(
        "observations/band/<int:band_number>/update/",
        Update1DPipelineAPI.as_view(),
    ),

    path(
        "tiles/band/<int:band_number>/update/",
        Update3DPipelineAPI.as_view(),
    ),
]