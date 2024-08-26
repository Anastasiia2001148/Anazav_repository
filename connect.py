import psycopg2
from contextlib import contextmanager

@contextmanager
def create_connection():
    try:
        conn = psycopg2.connect(host = 'localhost', database = 'test10', user = 'postgres', password = 'mysecretpassword')
        yield conn
        conn.close()
    except psycopg2.OperationalError as err:
        raise RuntimeError(f'Failed {err}')

