from airflow import DAG
from datetime import datetime, timedelta
import pendulum
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from datawarehouse.dwh import staging_table, core_table
from dataquality.soda import yt_elt_data_quality

from api.video_stats import (
    get_playlist_id,
    get_videos_id,
    extract_videos_data,
    save_data_to_json,
)

# Define the local timezone
local_tz = pendulum.timezone("Europe/Rome")

# Default Args
default_args = {
    "owner": "dataengineers",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "data@engineers.com",
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=5),
    "max_active_runs": 1,
    "dagrun_timeout": timedelta(hours=1),
    "start_date": datetime(2025, 1, 1, tzinfo=local_tz),
    # 'end_date': datetime(2030, 12, 31, tzinfo=local_tz),
}

#varables
staging_schema = "staging"
core_schema = "core"



#Produce Json
with DAG(
    dag_id="produce_json",
    default_args=default_args,
    description="A DAG to produce a JSON file with video stats from a YouTube channel",
    schedule="0 14 * * *",
    catchup=False,
) as dag :

    # defining the tasks
    # Define tasks
    playlist_id = get_playlist_id("MrBeast", "{{ var.value.API_KEY }}")
    video_ids = get_videos_id(playlist_id)
    extract_data = extract_videos_data(video_ids)
    save_to_json_task = save_data_to_json(extract_data)
    
    
    trigger_update_db = TriggerDagRunOperator(
        task_id="trigger_update_db",
        trigger_dag_id="update_db",
    )
    
    # Define dependencies
    playlist_id >> video_ids >> extract_data >> save_to_json_task>> trigger_update_db



# Update DB
with DAG(
    dag_id="update_db",
    default_args=default_args,
    description="DAG to process JSON file and update the staging and core tables in the data warehouse",
    schedule=None,
    catchup=False,
) as dag :

    # defining the tasks
    # Define tasks
    update_staging = staging_table()
    update_core = core_table()
    
    trigger_data_quality_checks = TriggerDagRunOperator(
        task_id="trigger_data_quality_checks",
        trigger_dag_id="data_quality_checks",
    )   
    
    # Define dependencies
    update_staging >> update_core >> trigger_data_quality_checks

# Data Quality Checks 
with DAG(
    dag_id="data_quality_checks",
    default_args=default_args,
    description="DAG to check data quality ",
    schedule=None,
    catchup=False,
) as dag :

    # defining the tasks
    # Define tasks
    soda_validation_staging = yt_elt_data_quality(staging_schema)
    soda_validation_core = yt_elt_data_quality(core_schema)
    
    # Define dependencies
    soda_validation_staging >> soda_validation_core  