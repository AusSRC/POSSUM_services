"""
Database query functions for 3d pipeline specific
"""
from .utils import *

def update_3d_pipeline_table(tile_number, band_number, status, column_name):
    """
    Update the 'tile_state_band{band_number}' table with given column name.
    Possible values for '3d_pipeline_ingest':
        - Ingested
        - IngestFailed
        _ IngestRunning
    Possible values for '3d_pipeline_val':
        - Running (Job has been submitted and is currently running)
        - Failed (Job failed to run)
        - WaitingForValidation (Job has finished running successfully, waiting for human validation)
        - Good/Bad (Currently has to be manually set after human validation)
    Possible values for '3d_pipeline':
        - A timestamp when the job has completed.

    Args:
    tile_number (str): The tile number to update.
    band_number (str): 1 or 2
    status (str): The status to set in the respective column.
    column_name (str) : The column to set.

    Return: 0 if tile was not found, 1 if successful
    """
    # validate params
    validate_band_number(band_number)
    if column_name not in (
        "3d_pipeline",
        "3d_pipeline_val",
        "3d_pipeline_ingest",
        "3d_val_link",
    ):
        raise ValueError(
            f"Updating {column_name} in possum.tile_state_band{band_number} is not allowed!"
        )
    print(
        f"Updating POSSUM tile database table for band{band_number} with {column_name} to {status}"
    )
    query = f"""
        UPDATE possum.tile_state_band{band_number}
        SET "{column_name}" = %s -- status
        WHERE tile = %s; -- tile_number
    """
    return execute_update_query(query, (status, tile_number))

def reset_3d_pipeline_val_waiting(band_number):
    """
    Update 3d_pipeline to null where 3d_pipeline_val = 'WaitingForValidation'
    """
    validate_band_number(band_number)    
    query = f"""
        UPDATE possum.tile_state_band1
        SET "3d_pipeline" = NULL
        WHERE "3d_pipeline_val" = 'WaitingForValidation'
    """
    return execute_update_query(query)

def reset_3d_pipeline_val_running(band_number):
    """
    Update 3d_pipeline_val to null where it's supposedly running
    """
    validate_band_number(band_number)    
    query = f"""
        UPDATE possum.tile_state_band1
        SET "3d_pipeline_val" = NULL
        WHERE "3d_pipeline_val" = 'Running'
    """
    return execute_update_query(query)

def reset_3d_pipeline_val_and_link_null(band_number):
    """
    Update 3d_pipeline_val and 3d_val_link to null WHERE 3d_pipeline is Null
    """
    validate_band_number(band_number)    
    query = f"""
        UPDATE possum.tile_state_band1
        SET "3d_pipeline_val" = Null, "3d_val_link" = Null
        WHERE "3d_pipeline" is NULL;
    """
    return execute_update_query(query)

def get_tiles_for_pipeline_run(band_number):
    """
    Get a list of tile numbers that should be ready to be processed by the 3D pipeline

    In the database, this is when:
    tile_state_band.cube_state = 'COMPLETED' and tile.3d_pipeline_val = [null]

    In POSSUM pipeline status sheet, this is the equivalent of:
    'aus_src' column is not empty and '3d_pipeline' column is empty for the given band number.

    Args:
    band_number (int): The band number (1 or 2) to check.

    Returns:
    list: A list of tile numbers that satisfy the conditions.
    """
    validate_band_number(band_number)
    print(
        f"Fetching tiles ready for 3D pipeline run for band {band_number} from the database."
    )
    query = f"""
        SELECT tile FROM possum.tile_state_band{band_number}
        WHERE UPPER(cube_state) = 'COMPLETED'
        AND UPPER(mfs_state) = 'COMPLETED'
        AND ("3d_pipeline_val" IS NULL OR TRIM("3d_pipeline_val") = '')
    """
    return execute_query(query)


def get_tiles_for_ingest(band_number):
    """
    Get a list of 3D pipeline tile numbers that should be ready to be ingested.
    i.e. tile_state_band1.'3d_pipeline_val' = 'Good' and
    tile_state_band1.'3d_pipeline_ingest' is NULL

    Args:
    band_number (int): The band number (1 or 2) to check.

    Returns:
    list: A list of tile numbers that satisfy the conditions.
    """
    validate_band_number(band_number)
    print(
        f"Fetching tiles ready for 3D pipeline run for band {band_number} from the database."
    )
    query = f"""
        SELECT DISTINCT tile
        FROM possum.tile_state_band{band_number} tile_3d
        WHERE LOWER(tile_3d."3d_pipeline_val") = 'good' AND
        (tile_3d."3d_pipeline_ingest" IS NULL OR
        TRIM(tile_3d."3d_pipeline_ingest") = '')
        ORDER BY tile
    """
    results = execute_query(query)
    # flatten tile ids into an array
    return [row[0] for row in results]

# Extra queries for direct querying from Lerato
def get_tiles_order_by_3d_pipeline_val(band_number):
    """
    ## check whole tile3d pipeline status database
    """
    validate_band_number(band_number)
    query = f"""
        SELECT tile_3d.*
        FROM possum.tile_state_band{band_number} AS tile_3d
        ORDER BY "3d_pipeline_val" ASC
    """
    return execute_query(query)


def get_tiles_for_completed_processing(band_number):
    """
    ## check tile3d for completed processing
    """
    validate_band_number(band_number)
    query = f"""
        SELECT tile_3d.*
        FROM possum.tile_state_band{band_number} AS tile_3d
        WHERE LOWER("3d_pipeline_val") = 'waitingforvalidation' OR LOWER("3d_pipeline_val") = 'good'
    """
    return execute_query(query)


def get_tiles_where_no_validation_link(band_number):
    """
    ## Select tiles where validation link doesnt exist
    """
    validate_band_number(band_number)
    query = f"""
        SELECT tile_3d.*
        FROM possum.tile_state_band{band_number} AS tile_3d
        WHERE "3d_pipeline" IS NOT NULL and "3d_pipeline_val" IS NULL
        ORDER BY "3d_pipeline" ASC
    """
    return execute_query(query)


def get_tiles_with_filter(band_number, column_name, column_value, order_by_3d_pipeline_ingest=True):
    """
    ## Select tiles with conditions
    """
    # validate allowed column names
    allowed_columns = ["3d_pipeline", "3d_pipeline_val", "3d_pipeline_ingest", "3d_val_link", "tile"]
    column_name = column_name.strip().lower()
    if column_name not in allowed_columns:
        raise ValueError(f"Column '{column_name}' is not allowed. Must be one of {allowed_columns}")
    query = f"""
        SELECT tile_3d.*
        FROM possum.tile_state_band{band_number} AS tile_3d
    """
    query +=  f' WHERE LOWER("{column_name}") = %s'
    if order_by_3d_pipeline_ingest:
        query += ' ORDER BY "3d_pipeline_ingest"'
       
    return execute_query(query, (column_value,))

def get_tiles_that_had_processing_started(band_number, tile_id):
    """
    ## Find tiles that had processing at least start
    """
    validate_band_number(band_number)
    query = f"""
        SELECT DISTINCT tile_3d.tile
        FROM possum.tile_state_band{band_number} tile_3d
        INNER JOIN possum.associated_tile ON associated_tile.tile = tile_3d.tile
        INNER JOIN possum.observation_state_band{band_number} ob ON ob.name = associated_tile.name
        WHERE UPPER(ob.cube_state) = 'COMPLETED'
        AND (tile_3d."3d_pipeline" IS NOT NULL)
    """
    params = ()
    if tile_id:
        query += " AND tile_3d.tile = %s"
        params = (tile_id,)
    query += " ORDER BY tile_3d.tile"
    return execute_query(query, params)


