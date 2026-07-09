"""
Database query functions for 1d pipeline specific queries
"""
from .utils import *

def find_boundary_issues(observation, band_number):
    """
    Check if there are any entries in partial_tile_1d_pipeline for the given observation
    where type indicates it crosses a projection boundary.
    This is to identify potential issues with tiles that cross projection boundaries.
    """
    validate_band_number(band_number)
    print(
        f"Checking for projection boundary issues for Observation: {observation}"
    )
    query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM possum.partial_tile_1d_pipeline_band{band_number}
            WHERE observation = %s AND LOWER(type) like '%%crosses projection boundary%%'
        ) AS match_found;
    """
    results = execute_query(query, (observation,), get_colnames=False)
    issues_found = results[0]
    print(f"Projection boundary issues found: {issues_found}")
    if issues_found is True:
        print("Boundary issues found.")
    else:
        print("No boundary issues found.")
    return issues_found


def update_partial_tile_1d_pipeline_status(
    field_name, tile_numbers, band_number, status
):
    """
    Update 1d_pipeline in partial_tile_1d_pipeline_band{band_number} table for a set of tiles.
    This replaces the 1d_pipeline column in the POSSUM pipeline validation Google sheet:
    Partial Tile Pipeline - regions - Band {band_number}

    Args:
    field_name (str): The field ID with 'EMU_' or 'WALLABY_' prefix.
    tile_numbers (tuple): The tile numbers to update.
    band_number: '1' or '2'
    status (str): The new validation status to set.
    """
    validate_band_number(band_number)

    print(
        f"Updating POSSUM partial_tile_1d_pipeline_band{band_number}.1d_pipeline in the database"
    )
    t1, t2, t3, t4 = tile_numbers
    query = f"""
        UPDATE possum.partial_tile_1d_pipeline_band{band_number}
        SET "1d_pipeline" = %s -- status
        WHERE observation = %s -- field_name
    """
    args = (status, field_name)
    # Check for NULLS in tile numbers and make sure the query says IS NULL and not = NULL so it works
    for i, tile in enumerate([t1, t2, t3, t4], start=1):
        if tile is None or tile.strip() == "":  # If tile is None, use IS NULL
            # put condition on newline
            query += f"\n AND tile{i} IS NULL"
        else:  # Otherwise, use equality
            # put condition on newline, careful with the commenting!
            query += f"\n AND tile{i} = %s -- tile"
            args = args + (tile,)

    row_num = execute_update_query(query, args)
    if row_num == 1:
        print(
            f"Updated row with tiles {tile_numbers} status to {status} in '1d_pipeline' column."
        )
    if row_num == 0:
        print(
            f"No matching row found to update for field {field_name} with tiles {tile_numbers}."
        )
        raise ValueError(
            f"Field {field_name} with tiles {tile_numbers} not found in the database d."
        )
    if row_num > 1:
        print(
            f"Warning: Multiple ({row_num}) rows updated for field {field_name} with tiles {tile_numbers}."
        )
        raise ValueError(
            f"Multiple ({row_num}) rows updated for field {field_name} with tiles {tile_numbers}."
        )
    return row_num


def reset_partial_tile_1d_pipeline(band_number, field_name):
    """
    Update database to rerun a field
    1. Clear the 1d_pipeline flag on the partial tile rows
    """
    validate_band_number(band_number)
    query = f"""
        UPDATE possum.partial_tile_1d_pipeline_band{band_number} AS pt
        SET "1d_pipeline" = NULL
        FROM possum.observation AS ob
        JOIN possum.observation_state_band{band_number} AS ob1
        ON ob.name = ob1.name
        WHERE ob.name = pt.observation
        AND ob1.name = %s
    """
    return execute_update_query(query, (field_name,))

def reset_running_jobs_not_running(band_number, field_name):
    """
    ## Clear running jobs that are not running
    """
    validate_band_number(band_number)
    query = f"""
        UPDATE possum.partial_tile_1d_pipeline_band{band_number} AS pt
        SET "1d_pipeline" = NULL
        FROM possum.observation AS ob
        JOIN possum.observation_state_band{band_number} AS ob1
        ON ob.name = ob1.name
        WHERE ob.name = pt.observation
        AND ob1.name = %s
        AND LOWER("1d_pipeline") = 'Running'
    """
    return execute_update_query(query, (field_name,))

def restart_running_jobs(band_number):
    """
    ## Update running jobs to Null so they get restarted
    """
    validate_band_number(band_number)
    query = f"""
        UPDATE possum.partial_tile_1d_pipeline_band{band_number} AS pt
        SET "1d_pipeline" = NULL
        WHERE LOWER("1d_pipeline") = 'running'
    """
    return execute_update_query(query)    

def update_partial_1d_pipeline_type_center():
    """
    ## Also update type from "center" to "center - crosses projection boundary!"
    """
    query = f"""
        UPDATE possum.partial_tile_1d_pipeline_band1 AS pt
        SET type = 'center - crosses projection boundary!'
        WHERE pt."1d_pipeline" = 'Failed'
        AND pt.type = 'center'
        RETURNING pt.observation, pt.tile1, pt.type, pt."1d_pipeline";
    """
    return execute_update_query(query)

def get_partial_tiles(band_number):
    """
    ## Check whole partial tile DB
    """
    validate_band_number(band_number)
    sql = f"""
    SELECT * 
    FROM possum.partial_tile_1d_pipeline_band{band_number}
    ORDER BY id DESC   
    """

    return execute_query(sql)

def get_partial_tiles_with_sbid(band_number):
    """
    Get partial tiles joined with observation table to get SBID
    """
    validate_band_number(band_number)
    sql = f"""
    SELECT p.*, o.sbid
    FROM possum.partial_tile_1d_pipeline_band{band_number} AS p
    LEFT JOIN possum.observation AS o ON p.observation = o.name 
    """

    return execute_query(sql)


def get_partial_tiles_for_1d_pipeline_run(band_number):
    """
    Get a list of partial tiles that should be ready to be processed by the 1D pipeline
    In the database, this is when:
    partial_tile_1d_pipeline_band{band_number}.sbid is not NULL, number_sources is not NULL,
    and 1d_pipeline is NULL

    Args:
    band_number (int): The band number (1 or 2) to check.

    Returns:
    list: A list of tuples containing (field_ID, sbid, (tile1, tile2, tile3, tile4))
    that satisfy the conditions.
    """
    validate_band_number(band_number)
    print(f"""Fetching partial tiles ready for 1D pipeline run for band {band_number}
          from the database.""")
    query = f"""
        SELECT pt.observation, ob.sbid, pt.tile1, pt.tile2, pt.tile3, pt.tile4
        FROM possum.partial_tile_1d_pipeline_band{band_number} pt,
        possum.observation ob
        WHERE ob.sbid IS NOT NULL AND TRIM(ob.sbid) != ''
          AND ob.name = pt.observation
          AND pt.number_sources IS NOT NULL
          AND (pt."1d_pipeline" IS NULL or TRIM(pt."1d_pipeline") = '')
        ORDER BY id;
    """
    # added order by id to have consistent ordering for tests
    return execute_query(query)


def check_partial_tile_for_observation_field(band_number, field_name, crosses_centre: False):
     """
     ## Check partial tile database for a field
     """ 

     validate_band_number(band_number)
     sql = f"""
        SELECT pt.observation, ob.sbid, pt.tile1, pt.tile2, pt.tile3, pt.tile4,
  		    pt.type, pt.number_sources, pt."1d_pipeline", ob1."1d_pipeline_validation"
        FROM possum.partial_tile_1d_pipeline_band{band_number} pt,
            possum.observation ob, possum.observation_state_band{band_number} as ob1
        WHERE ob.name = pt.observation AND ob.name = ob1.name
        AND ob.name = %s
     """
     params = (field_name,)
     if crosses_centre:
         sql += f""" AND LOWER("type") LIKE %s"""
         params += ('center - crosses%',)
     sql += " ORDER BY id DESC;"    

     return execute_query(sql, params)


def get_partial_tile_jobs_running(band_number):
    """
    ## Check database for running jobs, might be ghosts
    """
    validate_band_number(band_number)

    query = f"""
        SELECT pt.observation, ob.sbid, pt.tile1, pt.tile2, pt.tile3, pt.tile4,
   		pt.type, pt.number_sources, pt."1d_pipeline", ob1."1d_pipeline_validation"
        FROM possum.partial_tile_1d_pipeline_band{band_number} pt,
        possum.observation ob, possum.observation_state_band{band_number} as ob1
        WHERE ob.name = pt.observation AND ob.name = ob1.name
        AND LOWER(pt."1d_pipeline") = 'running'
        ORDER BY id DESC;
    """

    return execute_query(query)

def get_partial_tile_jobs_failed(band_number, centre_only: bool = False):
    """
    ## Check database for failed jobs, probably 12hr boundary if theyre center.
    """
    validate_band_number(band_number)
    query = f"""
        SELECT pt.observation, ob.sbid, pt.tile1, pt.tile2, pt.tile3, pt.tile4,
  		pt.type, pt.number_sources, pt."1d_pipeline", ob1."1d_pipeline_validation",
        t."ra_deg"
        FROM possum.partial_tile_1d_pipeline_band{band_number} pt,
        possum.observation ob, possum.observation_state_band{band_number} as ob1, possum.tile as t
        WHERE ob.name = pt.observation AND ob.name = ob1.name 
        AND t.tile = pt.tile1
        AND LOWER(pt."1d_pipeline") = 'failed'
    """
    if centre_only:
        query += """ AND LOWER(pt.type) = 'center'"""
    query += " ORDER BY id DESC;"
    return execute_query(query)

def get_partial_tile_by_tile_number(band_number, tile_number):
    """
    -- ## Check database for a tile number
    """
    validate_band_number(band_number)
    query = f"""
        SELECT pt.observation, ob.sbid, pt.tile1, pt.tile2, pt.tile3, pt.tile4,
          pt.type, pt.number_sources, pt."1d_pipeline", ob1."1d_pipeline_validation",
          t."ra_deg"
        FROM possum.partial_tile_1d_pipeline_band{band_number} pt,
          possum.observation ob, possum.observation_state_band{band_number} as ob1,
          possum.tile as t
        WHERE ob.name = pt.observation AND ob.name = ob1.name 
          AND t.tile = pt.tile1
          AND pt.tile1 = %s
        ORDER BY id DESC;
    """
    return execute_query(query, (tile_number,))

def get_partial_tiles_by_observation(band_number, fieldname, skip_boundary_issues):
    """
    For polarimetry github: summary_plot_1D_partial_tiles.py
    """
    validate_band_number(band_number)
    sql = f"""
            SELECT LOWER("1d_pipeline") AS "1d_pipeline", tile1, tile2, tile3, tile4
            FROM possum.partial_tile_1d_pipeline_band{band_number}
            WHERE observation = %s
          """
    params = (fieldname,)
    if skip_boundary_issues:
        sql += " AND LOWER(type) not like %s"
        params += ('%crosses projection boundary%', )

    return execute_query(sql, params)                 

def get_partial_tiles_with_hpx_edge(band_number):
    """
    ## Check partial tile database for hpx edge
    """
    validate_band_number(band_number)

    query = f"""
        SELECT pt.observation, ob.sbid, pt.tile1, pt.tile2, pt.tile3, pt.tile4,
  		  pt.type, pt.number_sources, pt."1d_pipeline", ob1."1d_pipeline_validation"
        FROM possum.partial_tile_1d_pipeline_band{band_number} pt,
          possum.observation ob, possum.observation_state_band{band_number} as ob1
        WHERE ob.name = pt.observation AND ob.name = ob1.name
          AND LOWER(ob1."1d_pipeline_validation") LIKE '%hpx edge%'
        ORDER BY id DESC;
    """
    return execute_query(query)

def get_partial_tile_constraints(band_number):
    """
    ## see constraints on partial_tile_1d_pipeline_band1
    """
    validate_band_number(band_number)

    query = f"""
            SELECT c.conname, pg_get_constraintdef(c.oid) AS definition
            FROM pg_constraint AS c
            JOIN pg_class AS t ON c.conrelid = t.oid
            JOIN pg_namespace AS n
            ON n.oid = t.relnamespace
            WHERE n.nspname = 'possum'
            AND t.relname = 'partial_tile_1d_pipeline_band{band_number}'
            AND c.contype = 'c';
    """
    return execute_query(query)
    
def get_observations_with_complete_partial_tiles(band_number):
    validate_band_number(band_number)

    """
    For each observation, check if all '1d_pipeline' is "Completed" and '1d_pipeline_validation' is empty
    Return rows of: (observation, sbid, all_complete)
    for which all_complete is True if all partial tiles for that observation and sbid
    have '1d_pipeline' marked as "Completed" and '1d_pipeline_validation' for the observation is NULL
    """
    sql = f"""
        SELECT pt.observation, ob1.sbid,
        CASE
            WHEN EXISTS (
                SELECT 1
                FROM possum.partial_tile_1d_pipeline_band{band_number} pt2
                WHERE pt2.observation = pt.observation
                AND (LOWER(pt2."1d_pipeline") != 'completed' OR pt2."1d_pipeline" IS NULL)
                ) THEN false
            WHEN (ob."1d_pipeline_validation" IS NULL OR TRIM(ob."1d_pipeline_validation") = '') AND LOWER(pt."1d_pipeline") = 'completed'
                THEN true
            ELSE
                false
        END AS all_complete
        FROM possum.partial_tile_1d_pipeline_band{band_number} pt, possum.observation_state_band{band_number} ob, possum.observation as ob1
        WHERE ob.name = pt.observation and ob1.name = ob.name
        GROUP BY pt.observation, ob1.sbid, ob."1d_pipeline_validation", pt."1d_pipeline";
    """
    return execute_query(sql)


def get_observations_non_edge_rows(band_number):
    """
    For each observation, check if all '1d_pipeline' is "Completed" and 1d_pipeline_validation' is empty,
    except if any partial tile type is an edge case (includes "crosses projection boundary").
    Return rows of: (observation, sbid, non_edge_complete)
    for which non_edge_complete is True if all partial tiles for that observation and sbid
    have '1d_pipeline' marked as "Completed" and '1d_pipeline_validation' for the observation is NULL
    disregarding those that have "crosses projection boundary" in its type.
    """
    validate_band_number(band_number)

    sql = f"""
    SELECT
        ob.name AS observation,
        ob.sbid,
        CASE
            WHEN
                -- Observation-level validation must be empty
                (obs."1d_pipeline_validation" IS NULL
                OR TRIM(obs."1d_pipeline_validation") = '')

                -- And there must be NO NON-boundary-crossing tile that is not completed
                -- i.e. all non-boundary-crossing tiles must be completed
                -- important to test for IS NULL because != 'completed' does not catch NULLs
                AND NOT EXISTS (
                    SELECT 1
                    FROM possum.partial_tile_1d_pipeline_band{band_number} pt2
                    WHERE pt2.observation = ob.name
                    AND LOWER(pt2.type) NOT LIKE '%crosses projection boundary%'
                    AND (LOWER(pt2."1d_pipeline") != 'completed' OR pt2."1d_pipeline" IS NULL)
                )

                -- And there must be at least one relevant tile at all
                -- otherwise, all complete would be true for observations not yet in the partial_tile_1d_pipeline_band table
                AND EXISTS (
                    SELECT 1
                    FROM possum.partial_tile_1d_pipeline_band{band_number} pt3
                    WHERE pt3.observation = ob.name
                    AND LOWER(pt3.type) NOT LIKE '%crosses projection boundary%'
                )
            THEN true
            ELSE false
        END AS all_complete
    FROM possum.observation ob
    JOIN possum.observation_state_band{band_number} obs
        ON obs.name = ob.name
    ORDER BY ob.sbid;
    """
    return execute_query(sql)


def get_fields_ready_single_SB_pipeline(band_number):
    """
    ## Check fields that could be added to partial tile database
    Get fields that are ready for 1D Partial Tile pipeline processing:
    i.e. single_sb_1d_pipeline is NULL/empty and cube_state = 'COMPLETED'

    returns a table with columns ["name"]
    """
    validate_band_number(band_number)

    sql = f"""
    SELECT name FROM possum.observation_state_band{band_number}
    WHERE ("single_sb_1d_pipeline" IS NULL or "single_sb_1d_pipeline" = '')
    AND UPPER("cube_state") = 'COMPLETED';
    """
    return execute_query(sql)



def get_full_table_single_SB_pipeline(band_number):
    """
    Get single_sb_1d_pipeline status as either raw rows 
    """
    validate_band_number(band_number)

    sql = f"""
        SELECT * FROM possum.observation_state_band{band_number}
    """
    return execute_query(sql)

def get_observation_by_name(band_number, name):
    """
    ## ## Check fields by observation name
    """
    validate_band_number(band_number)

    sql = f"""
    SELECT * 
    FROM possum.observation_state_band{band_number}
    WHERE "name" = %s
    """

    return execute_query(sql, (name,))

def get_observation_failed(band_number):
    """
    ## ## Check fields where validation / summary plot failed
    """
    validate_band_number(band_number)

    sql = f"""
    SELECT * 
    FROM possum.observation_state_band{band_number}
    WHERE LOWER("1d_pipeline_validation") = 'failed'
    """

    return execute_query(sql)

def get_observation_completed_aussrc(band_number):
    """
    ## Check total number of fields that AUSSRC has done
    """
    validate_band_number(band_number)

    sql = f"""    
            SELECT * FROM possum.observation_state_band{band_number}
            WHERE UPPER("cube_state") = 'COMPLETED'
    """
    return execute_query(sql)

def get_1d_partial_tiles_completed(band_number):
    """
    ## Check total number of fields that we've done in 1D partial tiles
    """
    validate_band_number(band_number)

    sql = f"""
            SELECT * FROM possum.observation_state_band{band_number}
            WHERE LOWER("1d_pipeline_validation") = 'completed'
    """
    return execute_query(sql)

def update_1d_pipeline_table(field_name, band_number, status, column_name):
    """
    Update the 1d_pipeline_validation or single_1d_pipeline column in the observation table.
    This is to the equivalent to POSSUM pipeline status sheet: Survey Fields - Band {band_number}

    Args:
    field_name       : observation.field_name
    band_number      : '1' or '2'
    status (str): The status to set in the 'status_column' column.
    column_name.     : The column to set

    """
    validate_band_number(band_number)
    if column_name.lower() not in ("1d_pipeline_validation", "single_sb_1d_pipeline"):
        raise ValueError(
            f"Not allowed to update {column_name} in observation_state_band{band_number}!"
        )
    print(
        f"Updating POSSUM observation_state_band{band_number} table with {column_name} status"
    )
    query = f"""
        UPDATE possum.observation_state_band{band_number}
        SET "{column_name}" = %s -- status
        WHERE name = %s; -- field_name
    """
    return execute_update_query(query, (status, field_name),)

def reset_1d_pipeline_validation_failed(band_number):
    """
    Reset failed the 1d_pipeline_validation column in the observation table to NULL.  
    """
    validate_band_number(band_number)    
    query = f"""
        UPDATE possum.observation_state_band{band_number}
        SET "1d_pipeline_validation" = NULL -- status
        WHERE LOWER("1d_pipeline_validation") = 'failed'
    """
    return execute_update_query(query)


def reset_1d_pipeline_failed(band_number):
    """
    ## Update ALL failed jobs to set 1d_pipeline_validation to null
    """
    validate_band_number(band_number)
    query = f"""
            UPDATE possum.observation_state_band{band_number} AS ob1
            SET "1d_pipeline_validation" = NULL
            FROM possum.observation AS ob
            JOIN possum.partial_tile_1d_pipeline_band{band_number} AS pt
            ON pt.observation = ob.name
            WHERE ob1.name = ob.name
            AND pt."1d_pipeline" = 'Failed'
            RETURNING ob1.name, ob1."1d_pipeline_validation";
    """
    return execute_update_query(query)

def insert_partial_tiles(field_name, tile1, tile2, tile3, tile4, type, num_sources, band_number):
    validate_band_number(band_number)
    sql = f"""
            INSERT INTO possum.partial_tile_1d_pipeline_band{band_number}
            (observation, tile1, tile2, tile3, tile4, type, number_sources)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            -- If row already exists, then don't overwrite
            ON CONFLICT (generated_key) DO NOTHING;
        """    
    args = (
            field_name,  # observation
            tile1 if tile1.isdigit() else None,  # tile_1,
            tile2 if tile2 and tile2.isdigit() else None,  # tile_2
            tile3 if tile3 and tile3.isdigit() else None,  # tile_3
            tile4 if tile3 and tile4.isdigit() else None,  # tile_4
            type,  # type
            num_sources if num_sources.isdigit() else None  # number_sources
    )
    return execute_update_query(sql, args)
    

