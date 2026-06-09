from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..services import (
    find_boundary_issues,
    update_partial_tile_1d_pipeline_status,
    get_partial_tiles_for_1d_pipeline_run,
    update_1d_pipeline_table,
    get_fields_ready_single_SB_pipeline,
    get_full_table_single_SB_pipeline,
    get_observations_with_complete_partial_tiles,
    get_observations_non_edge_rows,
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
    

@api_view(["POST"])
def update_partial_tile_status(request, band_number: int):
    try:
        field_name = request.data.get("field_name")
        tile_numbers = request.data.get("tile_numbers")
        status_value = request.data.get("status")

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
    

@api_view(["GET"])
def observations_complete_partial_tiles(request, band_number: int):
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

   
@api_view(["GET"])
def fields_ready_single_sb_pipeline(request, band_number: int):
    """
    Returns fields ready for 1D single SB pipeline processing
    """
    try:
        data = get_fields_ready_single_SB_pipeline(band_number)
        return Response(data, status=status.HTTP_200_OK)
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
        data = get_full_table_single_SB_pipeline(band_number)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )        
        

@api_view(["POST"])
def update_1d_pipeline_table(request, band_number, column_name, field_name, status):
    """
    Update 1d_pipeline_validation field in observation_state_band{band_number} table    
    """
    try:
        rows = update_1d_pipeline_table(
            field_name=field_name,
            band_number=band_number,
            status=status,
            column_name=column_name
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

