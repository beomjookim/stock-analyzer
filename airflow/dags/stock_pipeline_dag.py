from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2025, 3, 1),
    'retries': 1,
}

with DAG(
    dag_id='stock_short_term_pipeline',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    fetch_data = BashOperator(
        task_id='fetch_data',
        bash_command='docker exec spark-master python /opt/spark/src/data_collection/short_term/fetch_stock_data.py'
    )

    process_data = BashOperator(
        task_id='process_data',
        bash_command='docker exec spark-master python /opt/spark/src/data_processing/short_term/augment_data.py'
    )

    create_data_mart = BashOperator(
        task_id='create_data_mart',
        bash_command='docker exec bigquery python /opt/bigquery/data_mart_creation.py'
    )

    fetch_data >> process_data >> create_data_mart
