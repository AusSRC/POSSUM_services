from django.urls import path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from views.pipeline_1d import (
    find_boundary_issues,
    partial_tiles_ready_for_pipeline,
    update_partial_tile_status,
    observations_non_edge_rows,
    observations_complete_partial_tiles,
    full_single_sb_pipeline_table,
    fields_ready_single_sb_pipeline,
    Update1DPipelineAPI,
)

from views.pipeline_3d import (
    TilesReadyForIngestAPI,
    TilesReadyFor3DPipelineAPI,
    Update3DPipelineAPI,
)

urlpatterns = [
    # --- TOKEN related ---
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),

    # --- API docs ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),

    # ---- 3D endpoints ---
    path(
        "api/3d-pipeline/tiles/ready-for-ingest/band<int:band_number>/",
        TilesReadyForIngestAPI.as_view(),
    ),
    path(
        "api/3d-pipeline/tiles/ready-for-3d/band<int:band_number>/",
        TilesReadyFor3DPipelineAPI.as_view(),
    ),
    path(
        "api/3d-pipeline/band<int:band_number>/update/",
        Update3DPipelineAPI.as_view(),
    ),

    # --- 1D endpoints ---
    path(
        "api/1d-pipeline/band<int:band_number>/update/",
        Update1DPipelineAPI.as_view(),
    ),
    path(
        "api/1d-pipeline/single-sb/fields-ready/band<int:band_number>/",
        fields_ready_single_sb_pipeline,
        name="fields-ready-single-sb",
    ),
    path(
        "api/1d-pipeline/single-sb/full-table/band<int:band_number>/",
        full_single_sb_pipeline_table,
        name="full-single-sb-table",
    ),
    path(
        "api/1d-pipeline/observations/complete-partial-tiles/band<int:band_number>/",
        observations_complete_partial_tiles,
        name="observations-complete-partial-tiles",
    ),
    path(
        "api/1d-pipeline/observations/non-edge-rows/band<int:band_number>/",
        observations_non_edge_rows,
        name="observations-non-edge-rows",
    ),
    path(
        "api/1d-pipeline/partial-tiles/ready-for-pipeline/band<int:band_number>/",
        partial_tiles_ready_for_pipeline,
        name="partial-tiles-ready",
    ),
    path(
        "api/1d-pipeline/partial-tiles/status/band<int:band_number>/",
        update_partial_tile_status,
        name="update-partial-tile-status",
    ),
    path(
        "api/1d-pipeline/find-boundary-issues/band<int:band_number>/",
        find_boundary_issues,
        name="boundary-issues",
    ),
]