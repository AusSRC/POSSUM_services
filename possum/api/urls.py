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

from .views.pipeline_1d import (
    boundary_issues,
    partial_tiles_ready_for_pipeline,
    update_partial_tile_status,
    observations_non_edge_rows,
    observations_complete_partial_tiles,
    full_single_sb_pipeline_table,
    fields_ready_single_sb_pipeline,
    update_1d_pipeline_table
)

from .views.pipeline_3d import (
    TilesReadyForIngestAPI,
    TilesReadyFor3DPipelineAPI,
    Update3DPipelineAPI,
)

urlpatterns = [
    # --- TOKEN related ---
    path("token/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),

    # --- API docs ---
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),

    # ---- 3D endpoints ---
    path(
        "3d-pipeline/tiles/ready-for-ingest/band<int:band_number>/",
        TilesReadyForIngestAPI.as_view(),
    ),
    path(
        "3d-pipeline/tiles/ready-for-3d/band<int:band_number>/",
        TilesReadyFor3DPipelineAPI.as_view(),
    ),
    path(
        "3d-pipeline/band<int:band_number>/update/3d_pipeline/<str:tile_number>/<str:status>/",
        Update3DPipelineAPI.as_view(),
        name="3d-pipeline-update-3d-pipeline"
    ),
    path(
        "3d-pipeline/band<int:band_number>/update/3d_pipeline_val/<str:tile_number>/<str:status>/",
        Update3DPipelineAPI.as_view(),
        name="3d-pipeline-update-3d-pipeline-val"
    ),
    path(
        "3d-pipeline/band<int:band_number>/update/3d_pipeline_ingest/<str:tile_number>/<str:status>/",
        Update3DPipelineAPI.as_view(),
        name="3d-pipeline-update-3d-pipeline-ingest"
    ),
    path(
        "3d-pipeline/band<int:band_number>/update/3d_pipeline_link/<str:tile_number>/<str:status>/",
        Update3DPipelineAPI.as_view(),
        name="3d-pipeline-update-3d-pipeline-link"
    ),

    # --- 1D endpoints ---
    path(
        "1d-pipeline/band<int:band_number>/update/1d-pipeline-validation/<str:field_name>/<str:status>/",
        update_1d_pipeline_table,
        name="observation-state-band-update-1d-pipeline-validation"
    ),
    path(
        "1d-pipeline/band<int:band_number>/update/single-sb-1d-pipeline/<str:field_name>/<str:status>/",
        update_1d_pipeline_table,
        name="observation-state-band-update-single-sb-1d-pipeline"
    ),
    path(
        "1d-pipeline/single-sb/fields-ready/band<int:band_number>/",
        fields_ready_single_sb_pipeline,
        name="fields-ready-single-sb",
    ),
    path(
        "1d-pipeline/single-sb/full-table/band<int:band_number>/",
        full_single_sb_pipeline_table,
        name="full-single-sb-table",
    ),
    path(
        "1d-pipeline/observations/complete-partial-tiles/band<int:band_number>/",
        observations_complete_partial_tiles,
        name="observations-complete-partial-tiles",
    ),
    path(
        "1d-pipeline/observations/non-edge-rows/band<int:band_number>/",
        observations_non_edge_rows,
        name="observations-non-edge-rows",
    ),
    path(
        "1d-pipeline/partial-tiles/ready-for-pipeline/band<int:band_number>/",
        partial_tiles_ready_for_pipeline,
        name="partial-tiles-ready",
    ),
    path(
        "1d-pipeline/partial-tiles/status/band<int:band_number>/",
        update_partial_tile_status,
        name="update-partial-tile-status",
    ),
    path(
        "1d-pipeline/find-boundary-issues/band<int:band_number>/<str:observation>/",
        boundary_issues,
        name="find-boundary-issues",
    ),
]