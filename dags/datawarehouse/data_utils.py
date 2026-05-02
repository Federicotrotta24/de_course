from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import RealDictCursor



# Nombre de la tabla que se va a usar en los distintos schemas
table = 'yt_api'



def get_conn_cursor():
    # Crear un hook de Airflow para conectarse a Postgres usando la conexión configurada
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_elt", database='elt_db')
    # Abrir conexión real a la base de datos
    conn = hook.get_conn()
    # Crear cursor que devuelve filas como diccionarios
    cur = conn.cursor(cursor_factory=RealDictCursor)
    return cur, conn
    
def close_conn_cursor(cur, conn):  
    # Cierra el cursor y la conexión a la base de datos
    cur.close()
    conn.close()


def create_schema(schema):
    # crear conexión y cursor
    cur, conn = get_conn_cursor()
    # Crear el schema si no existe

    sql_schema = f"CREATE SCHEMA IF NOT EXISTS {schema};"
    cur.execute(sql_schema)
    
    
    #guardar cambios y cerrar conexión
    conn.commit()
    close_conn_cursor(cur, conn)
    

def create_table(schema):
    cur, conn = get_conn_cursor()
    
    # Si el schema es staging, crear tabla staging, si es core, crear tabla core
    if schema == "staging":
        table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            "video_id" VARCHAR PRIMARY KEY,
            "video_title" VARCHAR NOT NULL,
            "upload_date" TIMESTAMP NOT NULL,
            "duration" TEXT,
            "video_views" INT,
            view_count INTEGER,
            like_count INTEGER,
            comment_count INTEGER
        );
        """
    else:
        table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            "video_id" VARCHAR PRIMARY KEY,
            "video_title" VARCHAR NOT NULL,
            "upload_date" TIMESTAMP NOT NULL,
            "duration" TIME,
            "video_type" VARCHAR,
            "video_views" INT,
            view_count INTEGER,
            like_count INTEGER,
            comment_count INTEGER
        );
        """
    cur.execute(table_sql)
    
    conn.commit()
    close_conn_cursor(cur, conn)
    

def get_video_ids(cur, schema):
    # Traer todos los video_id ya existentes en la tabla para comparar con los nuevos datos y decidir si insertar, actualizar o eliminar
    cur.execute(f"""SELECT video_id FROM {schema}.{table};""")
    ids = cur.fetchall()
    
    video_ids = [row['video_id'] for row in ids]
    return video_ids
