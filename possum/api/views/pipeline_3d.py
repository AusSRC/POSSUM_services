from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..services.pipeline_3d import (
    get_tiles_for_ingest,
    get_tiles_for_pipeline_run,
    get_tiles_with_filter,
    get_tiles_for_completed_processing,
    get_tiles_order_by_3d_pipeline_val,
    get_tiles_where_no_validation_link,
    get_tiles_that_had_processing_started,
    reset_3d_pipeline_val_and_link_null,
    reset_3d_pipeline_val_running,
    reset_3d_pipeline_val_waiting,
    update_3d_pipeline_table,
)


@extend_schema(summary="Find tiles that had processing at least started",
    parameters=[
        OpenApiParameter(
            name="tile_number",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,  # <-- optional
            description="Tile number e.g. 10670. If omitted, all tiles are checked.",
        ),
    ]
)
@api_view(["GET"])
def tiles_that_had_processing_started(request, band_number):
    try:
        tile_id = request.GET.get("tile_id")
        tiles = get_tiles_that_had_processing_started(band_number, tile_id)
        return Response({
            "success": True,
            "tiles": tiles,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(summary="check whole tile3d pipeline status database")
@api_view(["GET"])
def tiles_order_by_3d_pipeline_val(request, band_number):
    try:
        tiles = get_tiles_order_by_3d_pipeline_val(band_number)
        return Response({
                "success": True,
                "band": band_number,
                "tiles": tiles,
            })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    

@extend_schema(summary="Select tiles where ingest running",
               parameters=[
                   OpenApiParameter(name="order_by_3d_pipeline_ingest", type=bool, location=OpenApiParameter.QUERY, required=False,
                         description="If true, return results ordered by 3d_pipeline_ingest")
               ])
@api_view(["GET"])
def tiles_for_ingest_running(request, band_number):
    try:
        ordered = request.GET.get("order_by_3d_pipeline_ingest", "").lower() == "true"
        tiles = get_tiles_with_filter(band_number, column_name='3d_pipeline_ingest', column_value='IngestRunning', order_by_3d_pipeline_ingest=ordered)
        return Response({
                "success": True,
                "band": band_number,
                "tiles": tiles,
            })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(summary="check tile3d for running jobs")
@api_view(["GET"])
def tiles_for_running_jobs(request, band_number):
    try:
        tiles = get_tiles_with_filter(band_number, column_name='3d_pipeline_val', column_value='running')
        return Response({
                "success": True,
                "band": band_number,
                "tiles": tiles,
            })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(summary="check tile3d for a specific tilenumber")
@api_view(["GET"])
def tiles_for_tile_id(request, band_number, tile_id):
    try:
        tiles = get_tiles_with_filter(band_number, column_name='tile', column_value=tile_id, order_by_3d_pipeline_ingest=False)
        return Response({
                "success": True,
                "band": band_number,
                "tiles": tiles,
            })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(summary="check tile3d for completed processing")
@api_view(["GET"])
def tiles_for_completed_processing(request, band_number):
    try:
        tiles = get_tiles_for_completed_processing(band_number)
        return Response({
                "success": True,
                "band": band_number,
                "tiles": tiles,
            })    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(summary="Select tiles where validation link doesnt exist")
@api_view(["GET"])
def tiles_where_validation_link_doesnt_exist(request, band_number):
    try:
        tiles = get_tiles_where_no_validation_link(band_number)
        return Response({
                "success": True,
                "band": band_number,
                "tiles": tiles,
            })    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(summary="Select tiles where ingest failed",
               parameters=[
                   OpenApiParameter(name="order_by_3d_pipeline_ingest", type=bool, location=OpenApiParameter.QUERY, required=False,
                         description="If true, return results ordered by 3d_pipeline_ingest")
               ])
@api_view(["GET"])
def tiles_where_ingest_failed(request, band_number):
    try:
        ordered = request.GET.get("order_by_3d_pipeline_ingest", "").lower() == "true"
        tiles = get_tiles_with_filter(band_number, order_by_3d_pipeline_ingest=ordered)
        return Response({
                "success": True,
                "band": band_number,
                "tiles": tiles,
            })
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
def tiles_ready_for_ingest(request, band_number):
    try:
        tiles = get_tiles_for_ingest(band_number)

        return Response({
            "success": True,
            "band": band_number,
            "tiles": tiles,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(summary="Find tiles to do with 3D pipeline, CUBE and MFS needs to be done")
@api_view(["GET"])
def tiles_ready_for_3dpipeline(request, band_number):
    try:
        tiles = get_tiles_for_pipeline_run(band_number)        
        return Response({
            "success": True,
            "band": band_number,
            "tiles": tiles,
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="tile_number", type=int, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name="3d_pipeline", type=str, location=OpenApiParameter.QUERY, required=False,
                         description="A timestamp e.g. 2025-11-25 19:43:29.286359. If omitted, status will be set to NULL")
    ]
)
@api_view(["PATCH"])
def update_3d_pipeline(request):
    try:
        band_number = request.query_params.get("band_number")
        tile_number = request.query_params.get("tile_number")
        status = request.query_params.get("3d_pipeline")
        rows = update_3d_pipeline_table(
            tile_number=tile_number,
            band_number=band_number,
            status=status,
            column_name="3d_pipeline"
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
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="tile_number", type=int, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name="3d_val_link", type=str, location=OpenApiParameter.QUERY, required=False,
                         description="Optional. If omitted, value will be set to NULL.")
    ]
)
@api_view(["PATCH"])
def update_3d_val_link(request):
    try:
        band_number = request.query_params.get("band_number")
        tile_number = request.query_params.get("tile_number")
        status = request.query_params.get("3d_val_link")
        rows = update_3d_pipeline_table(
            tile_number=tile_number,
            band_number=band_number,
            status=status,
            column_name="3d_val_link"
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
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="tile_number", type=int, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name="3d_pipeline_ingest", type=str, location=OpenApiParameter.QUERY, required=False,
                         description="Possible values: 'Ingested', 'IngestFailed', 'IngestRunning'."
                            " If omitted, value will be set to NULL.")
    ]                    
)
@api_view(["PATCH"])
def update_3d_pipeline_ingest(request):
    try:
        band_number = request.query_params.get("band_number")
        tile_number = request.query_params.get("tile_number")
        status = request.query_params.get("3d_pipeline_ingest")
        rows = update_3d_pipeline_table(
            tile_number=tile_number,
            band_number=band_number,
            status=status,
            column_name="3d_pipeline_ingest"
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
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="tile_number", type=int, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name="3d_pipeline_val", type=str, location=OpenApiParameter.QUERY, required=False,
                         description="Possible values: 'Running', 'Failed', 'WaitingForValidation', 'Good', 'Bad'."
                         " If omitted, value will be set to NULL")
    ]
)
@api_view(["PATCH"])
def update_3d_pipeline_val(request):
    try:
        band_number = request.query_params.get("band_number")
        tile_number = request.query_params.get("tile_number")
        status = request.query_params.get("3d_pipeline_val")
        rows = update_3d_pipeline_table(
            tile_number=tile_number,
            band_number=band_number,
            status=status,
            column_name="3d_pipeline_val"
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

@extend_schema(summary="Update 3d_pipeline to null where 3d_pipeline_val = 'WaitingForValidation'")
@api_view(["POST"])
def reset_3d_pipeline_val_waitingforvalidation(request, band_number):
    try:
        rows = reset_3d_pipeline_val_waiting(band_number)
        return Response({
            "success": True,
            "rows_updated": rows,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )   


@extend_schema(summary="Update 3d_pipeline_val to null where it's supposedly running")
@api_view(["POST"])
def reset_running_3d_pipeline_val(request, band_number):
    try:
        rows = reset_3d_pipeline_val_running(band_number)
        return Response({
            "success": True,
            "rows_updated": rows,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )  


@extend_schema(summary="Update 3d_pipeline_val and 3d_val_link to null WHERE 3d_pipeline is Null")
@api_view(["POST"])
def reset_3d_pipeline_val_and_link(request, band_number):
    try:
        rows = reset_3d_pipeline_val_and_link_null(band_number)
        return Response({
            "success": True,
            "rows_updated": rows,
        })
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )  
