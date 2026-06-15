"""
Database query functions for interacting with the ausSRC database.
"""
from astropy.table import Table
from django.db import connection


#---- Utilities methods -------

def rows_to_table(rows, colnames=None, dtype=None):
    """
    Convert a list of row tuples and column names into an astropy Table.
    """
    if not rows:
        # Empty table, but we might still know the column names
        return Table(names=colnames or [], dtype=dtype)

    if colnames is None:
        ncols = len(rows[0])
        colnames = [f"col{i}" for i in range(ncols)]

    return Table(rows=rows, names=colnames, dtype=dtype)


def execute_update_query(query, params=None, verbose=False):
    """
    Execute an update SQL query and return the number of rows affected.

    Args:
    query (str): The SQL query to execute.
    params (tuple): Optional parameters for the SQL query.

    Returns:
    list: The number of rows affected.
    """
    rows_affected = 0
    try:
        with connection.cursor() as cursor:
            # Execute the query
            if verbose:
                print(f"Executing database query: {query}")
                if params:
                    print(f"With parameters: {params}")
            cursor.execute(query, params)
            connection.commit()
            rows_affected = cursor.rowcount
            if verbose:
                print(f"{rows_affected} rows affected.")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    return rows_affected


def execute_query(
    query, params=None, verbose=False, return_colnames=False
):
    """
    Execute a SQL query and return the results.

    Args:
        query (str): The SQL query to execute.
        database_connection: An open DB-API 2.0 connection.
        params (tuple): Optional parameters for the SQL query.
        verbose (bool): If True, print the query before executing.
        return_colnames (bool): If True, also return the column names.

    Returns:
        list or (list, list): The results of the query, and optionally
        a list of column names.
    """
    results = []
    colnames = []
    try:
        with connection.cursor() as cursor:
            if verbose:
                if params:
                    print(f"Executing database query: {query} with {params}")
                else:
                    print(f"Executing database query: {query}")

            cursor.execute(query, params)

            if cursor.description is not None:
                colnames = [desc[0] for desc in cursor.description]
                results = cursor.fetchall()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

    if return_colnames:
        return results, colnames
    return results


def validate_band_number(band_number):
    """
    Making sure band number is valid
    """
    if str(band_number) not in ["1", "2"]:
        raise ValueError("band_number must be either 1 or 2")
 