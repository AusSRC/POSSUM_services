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
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)")
    ]
)
@api_view(["GET"])
def get_failed_observations(request,  band_number: int):
    """
    ## Check fields by observation name
    """
    try:
        data = get_observation_failed(band_number)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )    

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

@extend_schema(
    description="""
\n-- SELECT * FROM possum.observation_state_band1
\n-- WHERE UPPER("cube_state") = 'COMPLETED'"""
)
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

@extend_schema(
    description="""\nSELECT * FROM possum.observation_state_band1
                   \nWHERE ("single_sb_1d_pipeline" IS NULL or "single_sb_1d_pipeline" = '')
                   \nAND UPPER("cube_state") = 'COMPLETED'"""
)
@api_view(["GET"])
def fields_ready_single_sb_pipeline(request, band_number: int):
    """
    ## Check fields that could be added to partial tile database
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

@extend_schema(
    description="""
\nSELECT pt.observation, ob.sbid, pt.tile1, pt.tile2, pt.tile3, pt.tile4,
\n  		 pt.type, pt.number_sources, pt."1d_pipeline", ob1."1d_pipeline_validation"
\nFROM possum.partial_tile_1d_pipeline_band1 pt,
\n           possum.observation ob, possum.observation_state_band1 as ob1
\nWHERE ob.name = pt.observation AND ob.name = ob1.name
\n           AND pt."1d_pipeline" = 'Running'
\nORDER BY id DESC;"""
)    
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
    description="""
\nSELECT pt.observation, ob.sbid, pt.tile1, pt.tile2, pt.tile3, pt.tile4,
\n		 pt.type, pt.number_sources, pt."1d_pipeline", ob1."1d_pipeline_validation"
\n		 , t."ra_deg"
\nFROM possum.partial_tile_1d_pipeline_band1 pt,
\npossum.observation ob, possum.observation_state_band1 as ob1
\n, possum.tile as t
\nWHERE ob.name = pt.observation AND ob.name = ob1.name 
\nAND t.tile = pt.tile1
\nAND pt."1d_pipeline" = 'Failed' 
\n-- AND "type" = 'center'
\nORDER BY id DESC;"""
)    
@api_view(["GET"])
def partial_tiles_failed(request, band_number: int, center_only: bool):
    """
    -- ## Check database for failed jobs, probably 12hr boundary if theyre center.
    """
    try:
        rows = get_partial_tile_jobs_failed(band_number, center_only)
        return Response(rows, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(description="""
\nSELECT pt.observation, ob.sbid, pt.tile1, pt.tile2, pt.tile3, pt.tile4,
\n		 pt.type, pt.number_sources, pt."1d_pipeline", ob1."1d_pipeline_validation"
\n		 , t."ra_deg"
\nFROM possum.partial_tile_1d_pipeline_band1 pt,
\npossum.observation ob, possum.observation_state_band1 as ob1
\n, possum.tile as t
\nWHERE ob.name = pt.observation AND ob.name = ob1.name 
\nAND t.tile = pt.tile1
\nAND pt.tile1 = '6143'
\nORDER BY id DESC;""")
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

@extend_schema(description="""
\nSELECT * FROM possum.observation_state_band1
\nWHERE ("1d_pipeline_validation" = 'Completed')""")
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

@extend_schema(description="""
\nSELECT pt.observation, ob.sbid, pt.tile1, pt.tile2, pt.tile3, pt.tile4,
\n 		 pt.type, pt.number_sources, pt."1d_pipeline", ob1."1d_pipeline_validation"
\nFROM possum.partial_tile_1d_pipeline_band1 pt,
\npossum.observation ob, possum.observation_state_band1 as ob1
\nWHERE ob.name = pt.observation AND ob.name = ob1.name
\nAND ob1."1d_pipeline_validation" LIKE '%hpx edge%'
\nORDER BY id DESC;""")
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

@extend_schema(description="""
\n-- SELECT
\n--     c.conname,
\n--     pg_get_constraintdef(c.oid) AS definition
\n-- FROM pg_constraint AS c
\n-- JOIN pg_class AS t
\n--     ON c.conrelid = t.oid
\n-- JOIN pg_namespace AS n
\n--     ON n.oid = t.relnamespace
\n-- WHERE n.nspname = 'possum'
\n--   AND t.relname = 'partial_tile_1d_pipeline_band1'
\n--   AND c.contype = 'c';
             """)
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
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="field_name", type=str, location=OpenApiParameter.QUERY, required=True),
    ],
    description="""
\n-- -- -- ## Update database to rerun a field
\n-- -- 1) Clear the 1d_pipeline flag on the partial tile rows
\n-- UPDATE possum.partial_tile_1d_pipeline_band1 AS pt
\n-- SET "1d_pipeline" = NULL
\n-- FROM possum.observation AS ob
\n-- JOIN possum.observation_state_band1 AS ob1
\n--   ON ob.name = ob1.name
\n-- WHERE ob.name = pt.observation
\n--   AND ob1.name = 'EMU_1001-09B';
    """
)
@api_view(["POST"])
def clear_partial_tile_1d_pipeline(request):
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
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="field_name", type=str, location=OpenApiParameter.QUERY, required=True),
        OpenApiParameter(name="status", type=str, location=OpenApiParameter.QUERY, required=False,
                         description="Optional. If omitted, status will be set to NULL")
    ],
    description="""
    \n-- -- -- ## Update database to rerun a field
    \n-- -- 2) Clear the validation flag on the observation_state rows e.g.
    \n-- UPDATE possum.observation_state_band1 AS ob1
    \n-- SET "1d_pipeline_validation" = NULL
    \n-- WHERE ob1.name = 'EMU_0510-32';
    """
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
    
@extend_schema(
    description="""e.g.\n-- UPDATE possum.observation_state_band1 AS ob1
                   \n-- SET "1d_pipeline_validation" = NULL
                   \n-- WHERE "1d_pipeline_validation" = 'Failed'"""
)
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
    
@extend_schema(
    description="""
\n-- UPDATE possum.observation_state_band1 AS ob1
\n-- SET "1d_pipeline_validation" = NULL
\n-- FROM possum.observation AS ob
\n-- JOIN possum.partial_tile_1d_pipeline_band1 AS pt
\n--     ON pt.observation = ob.name
\n-- WHERE ob1.name = ob.name
\n--   AND pt."1d_pipeline" = 'Failed'
\n-- RETURNING ob1.name, ob1."1d_pipeline_validation";"""
)
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
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
        OpenApiParameter(name="field_name", type=str, location=OpenApiParameter.QUERY, required=True),
    ],    
    description="""
\n-- ## Clear running jobs that are not running
\n-- UPDATE possum.partial_tile_1d_pipeline_band1 AS pt
\n-- SET "1d_pipeline" = NULL
\n-- FROM possum.observation AS ob
\n-- JOIN possum.observation_state_band1 AS ob1
\n-- ON ob.name = ob1.name
\n-- WHERE ob.name = pt.observation
\n-- AND ob1.name = 'EMU_0522-09B'
\n-- AND "1d_pipeline" = 'Running'
     """
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
    parameters=[
        OpenApiParameter(name="band_number", type=int, location=OpenApiParameter.QUERY, required=True,
                         description="Band number (1 or 2)"),
    ],
    description="""
    \n-- -- Update running jobs to Null so they get restarted
    \n-- UPDATE possum.partial_tile_1d_pipeline_band1 AS pt
    \n-- SET "1d_pipeline" = Null
    \n-- WHERE "1d_pipeline" = 'Running'
    """
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
           

@api_view(["POST"])
def update_failed_partial_tiles_centre(request):
    """
\n-- -- ## Also update type from "center" to "center - crosses projection boundary!"
\n-- UPDATE possum.partial_tile_1d_pipeline_band1 AS pt
\n-- SET type = 'center - crosses projection boundary!'
\n-- WHERE pt."1d_pipeline" = 'Failed'
\n--   AND pt.type = 'center'
\n-- RETURNING pt.observation, pt.tile1, pt.type, pt."1d_pipeline";
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
