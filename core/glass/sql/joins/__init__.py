"""
Join Operations
"""


def join_to_get_aggattr(db, a, b, pk, fk, attr, otbl):
    """
    Join to tables

    Add Attribute from table B to table A
    The attribute will be the result of a SUM of all objects
    related to each pk
    """

    from glass.sql.q import q_to_ntbl

    q = (
        f"SELECT mtbl.*, jtbl.{attr} "
        f"FROM {a} AS mtbl "
        "LEFT JOIN ("
            f"SELECT {fk}, SUM({attr}) AS {attr} "
            f"FROM {b} GROUP BY {fk}"
        ") AS jtbl "
        f"ON mtbl.{pk} = jtbl.{fk}"
    )

    nt = q_to_ntbl(db, otbl, q, api='psql')

    return otbl

