"""
Database query functions for common queries
"""
from .utils import *

def get_observations(band_number):
    """
    Get all observations for a given band number.
    """
    validate_band_number(band_number)
    sql = f"""
       SELECT o.*, os.cube_state, os.mfs_state 
       FROM possum.observation o 
       LEFT JOIN possum.observation_state_band{band_number} os 
       ON o.name=os.name 
       WHERE band=%s
    """
    return execute_query(sql, (band_number,))

def get_tiles_and_observations(band_number):
    """
    Get all tiles and associated observations for a given band number.
    """
    validate_band_number(band_number)
    sql = f"""
       SELECT * FROM (
        SELECT tile, STRING_AGG(name, ',') as obs, COUNT(*) AS n_obs, 
        SUM(CASE WHEN cube_state='COMPLETED' THEN 1 ELSE 0 END) AS n_complete FROM (
          SELECT tile, o.name, os.cube_state FROM possum.associated_tile a
          LEFT JOIN possum.observation_state_band{band_number} os ON a.name = os.name
          LEFT JOIN possum.observation o ON o.name = os.name WHERE band=%s
        ) AS cube_state_completed
        GROUP BY tile
      ) t LEFT JOIN possum.tile_state_band1 ts ON ts.tile = t.tile
      LEFT JOIN possum.tile tile ON tile.tile = t.tile
      WHERE n_obs=n_complete
    """
    return execute_query(sql, (band_number,))

def get_all_tiles():
    """
    ## check main tile database
    """
    query = f"""
        SELECT * 
        FROM possum.tile
    """
    return execute_query(query)