import oracledb
import configparser

pool = None

def init_pool():
    global pool
    if pool is not None:
        return pool  

    config = configparser.ConfigParser()
    config.read('variaveis.ini')
    db_cfg = config['ProjetoPucc']

    dsn = (
        f"(DESCRIPTION=(ADDRESS=(PROTOCOL={db_cfg['PROTOCOL']})(HOST={db_cfg['HOST']})(PORT={db_cfg['PORT']}))"
        f"(CONNECT_DATA=(SERVER={db_cfg['SERVER']})(SERVICE_NAME={db_cfg['SERVICE_NAME']})))"
    )

    oracledb.init_oracle_client(lib_dir=db_cfg['INSTANT_CLIENT_PATH'])

    pool = oracledb.create_pool(
        user=db_cfg['USER'],
        password=db_cfg['PASSWORD'],
        dsn=dsn,
        min=4,
        max=4,
        increment=0
    )

    try:
        with pool.acquire() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM DUAL")
                result = cur.fetchone()
                print(f"Oracle connection pool test successful: {result[0]}")
    except Exception as e:
        print("Database connection test failed:", e)
        raise

    print("Oracle connection pool created and validated.")
    return pool


def get_connection():
    if pool is None:
        raise RuntimeError("Database pool not initialized. Call init_pool() first.")
    return pool.acquire()
