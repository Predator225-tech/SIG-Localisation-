from contextlib import contextmanager
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from app.config import settings

pool = ConnectionPool(conninfo=settings.database_url, min_size=1, max_size=10, kwargs={"row_factory": dict_row}, open=False)

def open_pool():
    pool.open()

def close_pool():
    if not pool.closed:
        pool.close()

@contextmanager
def connection():
    with pool.connection() as conn:
        yield conn
