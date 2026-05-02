from datawarehouse.data_utils import (
    get_conn_cursor,
    close_conn_cursor,
    create_schema,
    create_table,
    get_video_ids,
)

from datawarehouse.data_loading import load_path
from datawarehouse.data_modification import insert_rows, update_rows, delete_rows
from datawarehouse.data_transformation import transform_data

import logging
from airflow.decorators import task

logger = logging.getLogger(__name__)

table = "yt_api"


@task
def staging_table():
    """
    Carga los datos crudos del JSON en la tabla staging.yt_api.
    """

    schema = "staging"
    cur, conn = None, None

    try:
        # Abrimos conexión a Postgres
        cur, conn = get_conn_cursor()

        # Leemos el JSON generado previamente
        yt_data = load_path()

        # Creamos schema y tabla staging si no existen
        create_schema(schema)
        create_table(schema)

        # Obtenemos los video_id que ya existen en staging
        table_ids = get_video_ids(cur, schema)

        # Recorremos cada video del JSON
        for row in yt_data:

            # Si la tabla está vacía, insertamos directamente
            if len(table_ids) == 0:
                insert_rows(cur, conn, schema, row)

            else:
                # Si el video ya existe, lo actualizamos
                if row["video_id"] in table_ids:
                    update_rows(cur, conn, schema, row)

                # Si no existe, lo insertamos
                else:
                    insert_rows(cur, conn, schema, row)

        # IDs actuales del JSON
        ids_in_json = {row["video_id"] for row in yt_data}

        # IDs que están en la tabla pero ya no están en el JSON
        ids_to_delete = set(table_ids) - ids_in_json

        # Borramos filas obsoletas
        if ids_to_delete:
            delete_rows(cur, conn, schema, ids_to_delete)

        logger.info(f"{schema} table updated successfully.")

    except Exception as e:
        logger.error(f"Error updating {schema} table: {e}")
        raise e

    finally:
        if cur and conn:
            close_conn_cursor(cur, conn)


@task
def core_table():
    """
    Lee datos desde staging, los transforma y los carga en core.yt_api.
    """

    schema = "core"
    cur, conn = None, None

    try:
        # Abrimos conexión a Postgres
        cur, conn = get_conn_cursor()

        # Creamos schema y tabla core si no existen
        create_schema(schema)
        create_table(schema)

        # Obtenemos los video_id que ya existen en core
        table_ids = get_video_ids(cur, schema)

        # Leemos todos los datos crudos desde staging
        cur.execute(f"SELECT * FROM staging.{table};")
        rows = cur.fetchall()

        current_video_ids = set()

        # Recorremos cada fila de staging
        for row in rows:

            current_video_ids.add(row["video_id"])

            # Transformamos la fila antes de llevarla a core
            transformed_row = transform_data(row)

            # Si core está vacío, insertamos
            if len(table_ids) == 0:
                insert_rows(cur, conn, schema, transformed_row)

            else:
                # Si ya existe, actualizamos
                if transformed_row["video_id"] in table_ids:
                    update_rows(cur, conn, schema, transformed_row)

                # Si no existe, insertamos
                else:
                    insert_rows(cur, conn, schema, transformed_row)

        # IDs que están en core pero ya no están en staging
        ids_to_delete = set(table_ids) - current_video_ids

        if ids_to_delete:
            delete_rows(cur, conn, schema, ids_to_delete)

        logger.info(f"{schema} table updated successfully.")

    except Exception as e:
        logger.error(f"Error updating {schema} table: {e}")
        raise e

    finally:
        if cur and conn:
            close_conn_cursor(cur, conn)