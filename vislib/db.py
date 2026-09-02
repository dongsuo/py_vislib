"""Connect to users' own external databases (MySQL or PostgreSQL).

The app's own DB is PostgreSQL (Neon), but each ``SourceDataBase`` record
points at a user's independent database, which may be either MySQL or
PostgreSQL. ``execSql`` / ``sourceTables`` call into this module so they
support both kinds — the dispatch is driven by ``SourceDataBase.db_type``.

Both drivers return rows as ``list[dict]`` mapping column-name -> value,
with ``bytes`` decoded to ``str`` so the result is JSON-serialisable.
"""

from MySQLdb import _mysql
import psycopg2


def _decode(value):
    """Normalise a cell value from either driver into JSON-safe Python."""
    if isinstance(value, bytes):
        return value.decode('utf-8', 'ignore')
    return value


def _run_mysql(host, port, user, password, database, sql):
    """Run SQL on a MySQL user database; return list[dict] (one per row)."""
    # mysqlclient 2.2+ dropped the legacy `passwd`/`db` kwargs (deprecated
    # since 1.3.8); only `password`/`database` are accepted now. These names
    # also work on older mysqlclient (1.3.8+), so they're the safe choice.
    db = _mysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
    )
    try:
        db.query(sql)
        data = db.store_result().fetch_row(maxrows=0, how=2)
    finally:
        db.close()
    # _mysql with how=2 keys columns as "table.column" when qualified; keep
    # only the column part so callers get a stable key.
    rows = []
    for index in range(len(data)):
        row = data[index]
        record = {}
        for key in row:
            column = key.split('.', 1)[1] if key.find('.') > 0 else key
            record[column] = _decode(row[key])
        rows.append(record)
    return rows


def _run_postgres(host, port, user, password, database, sql):
    """Run SQL on a PostgreSQL user database; return list[dict] (one per row)."""
    conn = psycopg2.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        dbname=database,
        connect_timeout=30,
    )
    # Match MySQL's autocommit behaviour so DDL/DML run via execSql actually
    # persists (psycopg2 otherwise rolls back uncommitted work on close).
    conn.autocommit = True
    try:
        cur = conn.cursor()
        cur.execute(sql)
        if cur.description is not None:
            columns = [desc[0] for desc in cur.description]
            raw_rows = cur.fetchall()
        else:
            columns, raw_rows = [], []
        cur.close()
    finally:
        conn.close()
    return [
        {col: _decode(val) for col, val in zip(columns, row)}
        for row in raw_rows
    ]


def run_sql(db_type, host, port, user, password, database, sql):
    """Dispatch to the right driver based on db_type. Returns list[dict]."""
    if str(db_type).lower() == 'postgres':
        return _run_postgres(host, port, user, password, database, sql)
    return _run_mysql(host, port, user, password, database, sql)


def list_tables(db_type, host, port, user, password, database):
    """List user tables in the external database. Returns list[str]."""
    if str(db_type).lower() == 'postgres':
        rows = _run_postgres(
            host, port, user, password, database,
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name;",
        )
        return [r['table_name'] for r in rows]
    rows = _run_mysql(host, port, user, password, database, 'show tables;')
    # MySQL's "show tables" returns one column keyed "Tables_in_<db>".
    return [list(r.values())[0] for r in rows]
