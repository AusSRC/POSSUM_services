from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..services.pipeline_1d import (
    find_boundary_issues,
    update_partial_tile_1d_pipeline_status,
    get_partial_tiles,
    get_partial_tiles_for_1d_pipeline_run,
    get_partial_tile_jobs_running,
    get_partial_tile_jobs_failed,
    get_partial_tile_by_tile_number,
    get_partial_tiles_with_hpx_edge,
    get_partial_tile_constraints,
    get_1d_partial_tiles_completed,
    check_partial_tile_for_observation_field,
    update_1d_pipeline_table,
    reset_1d_pipeline_validation_failed,
    reset_1d_pipeline_failed,
    reset_partial_tile_1d_pipeline,
    reset_running_jobs_not_running,
    restart_running_jobs,
    update_partial_1d_pipeline_type_center,
    get_fields_ready_single_SB_pipeline,
    get_full_table_single_SB_pipeline,
    get_observations_with_complete_partial_tiles,
    get_observations_non_edge_rows,
    get_observation_by_name,
    get_observation_failed,
    get_observation_completed_aussrc
)


@api_view(["GET"])
def partial_tiles(request, band_number: int):
    try:
        data = get_partial_tiles(band_number)
        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(["GET"])
def partial_tiles_ready_for_pipeline(request, band_number: int):
    try:
        data = get_partial_tiles_for_1d_pipeline_run(band_number)
        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@extend_schema(
    summary="Check partial tiles for an observation field",
    parameters=[
        OpenApiParameter(
            name="band_number",
            type=int,
            location=OpenApiParameter.PATH,
            description="Band number (1 or 2)",
        ),
        OpenApiParameter(
            name="field_name",
            type=str,
            location=OpenApiParameter.PATH,
            description="Name of the observation field to check."
        ),
        OpenApiParameter(
            name="crosses_centre",
            type=bool,
            location=OpenApiParameter.PATH,
            description="If true, only return observations whose type starts with 'center - crosses'."
        ),
    ]
)
@api_view(["GET"])
def check_partial_tiles_for_observation(request, band_number: int, field_name: str, crosses_centre: bool):
    """
    ## Check partial tile database for a field
    """
    try:
        data = check_partial_tile_for_observation_field(band_number, field_name, crosses_centre)
        return Response(data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )  

@extend_schema(
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="field_name", type=str, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name="tile_numbers", type=str, location=OpenApiParameter.QUERY, required=True,
                         description="Comma-separated list of tile numbers (e.g. '1,2,3,4')"),
        OpenApiParameter(name="status", type=str, location=OpenApiParameter.QUERY, required=True,
                         description="Status to set for the tiles, e.g. 'Completed'")
    ]
)
@api_view(["POST"])
def update_partial_tile_status(request):
    try:
        band_number = request.query_params.get("band_number")
        field_name = request.query_params.get("field_name")
        tile_numbers = request.query_params.get("tile_numbers")
        status_value = request.query_params.get("status")

        if not field_name or not tile_numbers or status_value is None:
            return Response(
                {"error": "field_name, tile_numbers, and status are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rows_updated = update_partial_tile_1d_pipeline_status(
            field_name,
            tuple(tile_numbers),
            band_number,
            status_value,
        )

        return Response(
            {
                "rows_updated": rows_updated,
                "message": "Update completed",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@extend_schema(
    summary="Check fields by observation name",
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="name", type=str, location=OpenApiParameter.QUERY, required=True),
    ]
)
@api_view(["GET"])
def observation_by_name(request,  band_number: int, name: str):
    """
    ## Check fields by observation name
    """
    try:
        data = get_observation_by_name(band_number, name)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@extend_schema(
    summary="## Check fields where validation / summary plot failed",
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)")
    ]
)
@api_view(["GET"])
def get_failed_observations(request,  band_number: int):
    """
    ## Check fields where validation / summary plot failed
    """
    try:
        data = get_observation_failed(band_number)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )    

@extend_schema(summary="## Check tiles TODO for validation")
@api_view(["GET"])
def observations_complete_partial_tiles(request, band_number: int):
    """
    ## Check tiles TODO for validation
    """
    try:
        data = get_observations_with_complete_partial_tiles(band_number)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def observations_non_edge_rows(request, band_number: int):
    try:
        data = get_observations_non_edge_rows(band_number)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(summary="## Check total number of fields that AUSSRC has done")
@api_view(["GET"])
def observations_completed_aussrc(request, band_number: int):
    try:
        """## Check total number of fields that AUSSRC has done"""
        data = get_observation_completed_aussrc(band_number)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
def boundary_issues(request, observation, band_number):
    """
    Returns True/False if boundary issues are found for the given observation
    """
    try:
        data = find_boundary_issues(observation, band_number)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(summary="## Check fields that could be added to partial tile database")
@api_view(["GET"])
def fields_ready_single_sb_pipeline(request, band_number: int):
    """
    ## Check fields that could be added to partial tile database
    """
    try:
        rows = get_fields_ready_single_SB_pipeline(band_number)
        return Response(rows, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def full_single_sb_pipeline_table(request, band_number: int):
    """
    Returns full observation state table for a band
    """
    try:
        rows = get_full_table_single_SB_pipeline(band_number)
        return Response(rows, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )        

@extend_schema(summary="## Check database for running jobs, might be ghosts")    
@api_view(["GET"])
def partial_tiles_running(request, band_number: int):
    """ 
    -- ## Check database for running jobs, might be ghosts
    """
    try:
        rows = get_partial_tile_jobs_running(band_number)
        return Response(rows, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    summary="## Check database for failed jobs, probably 12hr boundary if theyre center.",
    parameters=[
        OpenApiParameter(name="center_only", type=bool, location=OpenApiParameter.QUERY, required=False,
                         description="If true, only return observations whose type is 'center'.")
    ]
)    
@api_view(["GET"])
def partial_tiles_failed(request, band_number: int):
    """
    -- ## Check database for failed jobs, probably 12hr boundary if theyre center.
    """
    try:
        center_only = request.GET.get("center_only", "").lower() == "true"
        rows = get_partial_tile_jobs_failed(band_number, center_only)
        return Response(rows, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(summary="## Check database for a tile number")
@api_view(["GET"])
def partial_tiles_by_tile_number(request, band_number: int, tile_number: int):
    """
    -- ## Check database for a tile number
    """
    try:
        rows = get_partial_tile_by_tile_number(band_number=band_number, tile_number=tile_number)
        return Response(rows, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(summary="## Check total number of fields that we've done in 1D partial tiles")
@api_view(["GET"])    
def partial_tiles_completed(request, band_number: int):
    """
    -- ## Check total number of fields that we've done in 1D partial tiles
    """
    try:
        rows = get_1d_partial_tiles_completed(band_number)
        return Response(rows, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )   

@extend_schema(summary="## Check partial tile database for hpx edge")
@api_view(["GET"])
def partial_tiles_hpx_edge(request, band_number: int):
    """
    ## Check partial tile database for hpx edge
    """
    try:
        results = get_partial_tiles_with_hpx_edge(band_number)
        return Response(results, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(summary="## see constraints on partial_tile_1d_pipeline_band1")
@api_view(["GET"])
def partial_tiles_constraints(request, band_number: int):
    """
    ## see constraints on partial_tile_1d_pipeline_band1
    """
    try:
        results = get_partial_tile_constraints(band_number)
        return Response(results, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@extend_schema(
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="field_name", type=str, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name="status", type=str, location=OpenApiParameter.QUERY, required=False,
                         description="Optional. If omitted, status will be set to NULL")
    ]
)
@api_view(["PATCH"])
def update_single_sb_1d_pipeline(request):
    """
    Update single_sb_1d_pipeline field in observation_state_band{band_number} table    
    """
    try:
        band_number = request.query_params.get("band_number")
        field_name = request.query_params.get("field_name")
        status = request.query_params.get("status") 
        rows = update_1d_pipeline_table(
            field_name=field_name,
            band_number=band_number,
            status=status,
            column_name='single_sb_1d_pipeline'
        )

        return Response({
            "success": True,
            "rows_updated": rows,
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(
    summary="""
    \nUpdate database to rerun a field
    \n1. Clear the 1d_pipeline flag on the partial tile rows
    """,
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="field_name", type=str, location=OpenApiParameter.QUERY, required=True),
    ]
)
@api_view(["POST"])
def clear_partial_tile_1d_pipeline(request ):
    try:
        band_number = request.query_params.get("band_number")
        field_name = request.query_params.get("field_name")
        data = reset_partial_tile_1d_pipeline(band_number, field_name)
        return Response({"rows_updated": data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@extend_schema(
    summary="2) Clear the validation flag on the observation_state rows",
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="field_name", type=str, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name="status", type=str, location=OpenApiParameter.QUERY, required=False,
                         description="Optional. If omitted, status will be set to NULL")
    ]
)
@api_view(["PATCH"])
def update_1d_pipeline_validation(request):
    """
    2) Clear the validation flag on the observation_state rows
    """
    try:
        band_number = request.query_params.get("band_number")
        field_name = request.query_params.get("field_name")
        status = request.query_params.get("status") 
        rows = update_1d_pipeline_table(
            field_name=field_name,
            band_number=band_number,
            status=status,
            column_name='1d_pipeline_validation'
        )

        return Response({
            "success": True,
            "rows_updated": rows,
        })

    except Exception as e:
        return Response(


            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(summary="Clear the validation flag for failed observation_state rows")    
@api_view(["POST"])
def reset_failed_1d_pipeline_validation(request):
    """
    Clear the validation flag for failed observation_state rows    
    """
    try:
        band_number = request.query_params.get("band_number")
        rows = reset_1d_pipeline_validation_failed(band_number)

        return Response({
            "success": True,
            "rows_updated": rows,
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(summary="## Update ALL failed jobs to set 1d_pipeline_validation to null")    
@api_view(["POST"])
def reset_failed_1d_pipeline(request):
    """
    ## Update ALL failed jobs to set 1d_pipeline_validation to null
    """
    try:
        band_number = request.query_params.get("band_number")
        rows = reset_1d_pipeline_failed(band_number)
        return Response({
            "success": True,
            "rows_updated": rows,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    
@extend_schema(
    summary="## Clear running jobs that are not running",
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="field_name", type=str, location=OpenApiParameter.QUERY, required=True),
    ]
)
@api_view(["PATCH"])
def clear_running_jobs_not_running(request):
    """
    Clear running jobs that are not running
    """
    try:
        band_number = request.query_params.get("band_number")
        field_name = request.query_params.get("field_name")
        rows = reset_running_jobs_not_running(band_number, field_name)

        return Response({
            "success": True,
            "rows_updated": rows,
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )        

@extend_schema(
    summary="# -- -- Update running jobs to Null so they get restarted",
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
    ]
)    
@api_view(["POST"])
def restart_running_jobs_view(request):
    """
    # -- -- Update running jobs to Null so they get restarted
    """
    try:
        band_number = request.query_params.get("band_number")
        rows = restart_running_jobs(band_number)
        return Response({
            "success": True,
            "rows_updated": rows,
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )        
           
@extend_schema(summary='## Also update type from "center" to "center - crosses projection boundary!"')
@api_view(["POST"])
def update_failed_partial_tiles_centre(request):
    """
    ## Also update type from "center" to "center - crosses projection boundary!"
    """
    try:
        rows = update_partial_1d_pipeline_type_center()
        return Response({
            "success": True,
            "rows_updated": rows,
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )    
