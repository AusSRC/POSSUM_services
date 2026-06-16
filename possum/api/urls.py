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
    partial_tiles,
    partial_tiles_by_tile_number,
    partial_tiles_running,
    partial_tiles_failed,
    partial_tiles_completed,
    partial_tiles_hpx_edge,
    partial_tiles_constraints,
    partial_tiles_ready_for_pipeline,
    update_partial_tile_status,
    observation_by_name,
    get_failed_observations,
    observations_non_edge_rows,
    observations_complete_partial_tiles,
    observations_completed_aussrc,
    full_single_sb_pipeline_table,
    fields_ready_single_sb_pipeline,
    clear_partial_tile_1d_pipeline,
    update_1d_pipeline_validation,
    update_single_sb_1d_pipeline,
    reset_failed_1d_pipeline_validation,
    reset_failed_1d_pipeline,
    clear_running_jobs_not_running,
    restart_running_jobs_view,
    update_failed_partial_tiles_centre
)

from .views.pipeline_3d import (
    tiles_ready_for_ingest,
    tiles_ready_for_3dpipeline,
    update_3d_pipeline,
    update_3d_pipeline_val,
    update_3d_pipeline_ingest,
    update_3d_val_link,
    reset_running_3d_pipeline_val,
    reset_3d_pipeline_val_waitingforvalidation,
    reset_3d_pipeline_val_and_link
)

from .views.pipeline_common import (
    observations,
    tiles,
    tiles_observations
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
        tiles_ready_for_ingest,
        name="3d-pipeline-tiles-ready-for-ingest"
    ),
    path(
        "3d-pipeline/tiles/ready-for-3d/band<int:band_number>/",
        tiles_ready_for_3dpipeline,
        name="3d-pipeline-tiles-ready-for-3d"
    ),
    path(
        "3d-pipeline/tiles/update/3d_pipeline/",
        update_3d_pipeline,
        name="3d-pipeline-update-3d-pipeline"
    ),
    path(
        "3d-pipeline/tiles/update/3d_pipeline_val/",
        update_3d_pipeline_val,
        name="3d-pipeline-update-3d-pipeline-val"
    ),
    path(
        "3d-pipeline/tiles/update/3d_pipeline_ingest/",
        update_3d_pipeline_ingest,
        name="3d-pipeline-update-3d-pipeline-ingest"
    ),
    path(
        "3d-pipeline/tiles/update/3d_val_link/",
        update_3d_val_link,
        name="3d-pipeline-update-3d-val-link"
    ),
    path(
        "3d-pipeline/tiles/reset/3d_pipeline_val/running/band<int:band_number>/",
        reset_running_3d_pipeline_val,
        name="3d-pipeline-reset-3d-pipeline-val-running"
    ),
    path(
        "3d-pipeline/tiles/reset/3d_pipeline_val/waitingforvalidation/band<int:band_number>/",
        reset_3d_pipeline_val_waitingforvalidation,
        name="3d-pipeline-reset-3d-pipeline-val-waitingforvalidation"
    ),
    path(
        "3d-pipeline/tiles/reset/3d_pipeline_val/3d_val_link/band<int:band_number>/",
        reset_3d_pipeline_val_and_link,
        name="3d-pipeline-update-3d-val-link"
    ),

    # --- 1D endpoints ---   
    path(
        "1d-pipeline/observations/update/1d-pipeline-validation/",
        update_1d_pipeline_validation,
        name="observation-state-band-update-1d-pipeline-validation"
    ),
    path(
        "1d-pipeline/observations/reset/1d-pipeline-validation/",
        reset_failed_1d_pipeline_validation,
        name="observation-state-band-reset-1d-pipeline-validation"
    ), 
    path(
        "1d-pipeline/observations/reset/1d-pipeline/",
        reset_failed_1d_pipeline,
        name="observation-state-band-reset-1d-pipeline"
    ),    
    path(
        "1d-pipeline/observations/update/single-sb-1d-pipeline/",
        update_single_sb_1d_pipeline,
        name="observation-state-band-update-single-sb-1d-pipeline"
    ),
    path(
        "1d-pipeline/observations/single-sb-1d-pipeline/fields-ready/band<int:band_number>/",
        fields_ready_single_sb_pipeline,
        name="fields-ready-single-sb",
    ),
    path(
        "1d-pipeline/observations/single-sb-1d-pipeline/full-table/band<int:band_number>/",
        full_single_sb_pipeline_table,
        name="full-single-sb-table",
    ),
    path(
        "1d-pipeline/observations/failed/band<int:band_number>/",
        get_failed_observations,
        name="observations-failed",
    ),
    path(
        "1d-pipeline/observations/band<int:band_number>/name/<str:name>/",
        observation_by_name,
        name="observations-by-name",
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
        "1d-pipeline/observations/cube-state/completed/band<int:band_number>/",
        observations_completed_aussrc,
        name="observations-completed-aussrc"
    ),
    path(
        "1d-pipeline/partial-tiles/completed/band<int:band_number>/",
        partial_tiles_completed,
        name="partial-tiles-completed"
    ),
    path(
        "1d-pipeline/partial-tiles/band<int:band_number>/",
        partial_tiles,
        name="partial-tiles-all",
    ),
    path(
        "1d-pipeline/partial-tiles/band<int:band_number>/<int:tile_number>/",
        partial_tiles_by_tile_number,
        name="partial-tiles-by-tile-number",
    ),
    path(
        "1d-pipeline/partial-tiles/running/band<int:band_number>/",
        partial_tiles_running,
        name="check_running_partial_tile_jobs",
    ),
    path(
        "1d-pipeline/partial-tiles/failed/band<int:band_number>",
        partial_tiles_failed,
        name="check_failed_partial_tile_jobs",
    ),
    path(
        "1d-pipeline/partial-tiles/hpx-edge/band<int:band_number>/",
        partial_tiles_hpx_edge,
        name="check_partial_tiles_with_hpx_edge",
    ),
    path(
        "1d-pipeline/partial-tiles/constraints/band<int:band_number>/",
        partial_tiles_constraints,
        name="check_partial_tiles_constraints"
    ),
    path(
        "1d-pipeline/partial-tiles/ready-for-pipeline/band<int:band_number>/",
        partial_tiles_ready_for_pipeline,
        name="partial-tiles-ready",
    ),
    path(
        "1d-pipeline/partial-tiles/boundary-issues/band<int:band_number>/<str:observation>/",
        boundary_issues,
        name="find-boundary-issues",
    ),
    path(
        "1d-pipeline/partial-tiles/reset/1d-pipeline/",
        clear_partial_tile_1d_pipeline,
        name="partial-tile-clear-1d-pipeline"
    ), 
    path(
        "1d-pipeline/partial-tiles/reset/running-jobs/",
        clear_running_jobs_not_running,
        name="partial-tiles-clear-running-jobs"
    ),
    path(
        "1d-pipeline/partial-tiles/reset/restart-running-jobs/",
        restart_running_jobs_view,
        name="partial-tiles-restart-running-jobs"
    ),
    path(
        "1d-pipeline/partial-tiles/update/status/",
        update_partial_tile_status,
        name="update-partial-tiles-status",
    ),
    path(
        "1d-pipeline/partial-tiles/update/type/center/",
        update_failed_partial_tiles_centre,
        name="update-partial-tiles-type-center"
    ), 

    #---- Common URLS non specific to 1D and 3D ---
    path(
        "common/tiles/band<int:band_number>/",
        tiles,
        name="all-tiles"
    ),
    path(
        "common/tiles-observations/band<int:band_number>/",
        tiles_observations,
        name="tiles-associated-observations"
    ),
    path(
        "common/observations/band<int:band_number>/",
        observations,
        name="observations"
    ),



]