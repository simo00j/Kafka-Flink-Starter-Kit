from dataclasses import asdict, dataclass, field
from typing import List, Tuple

from jinja2 import Environment, FileSystemLoader
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from configs import get_sql_query, get_execution_environment, StreamJobConfig


def run_product_update_job(
    t_env: StreamTableEnvironment,
    get_sql_query=get_sql_query,
) -> None:
    # Create Source Tables
    t_env.execute_sql(get_sql_query('updates'))

    # Create Sink Tables
    t_env.execute_sql(get_sql_query('products', 'sink'))

    # Run Processing Query
    processing_query = get_sql_query('update_products', 'process')
    t_env.execute_sql(processing_query)
    print("Product Update Job started.")


def run_user_event_processing_job(
    t_env: StreamTableEnvironment,
    get_sql_query=get_sql_query,
) -> None:
    # Create Source Tables
    t_env.execute_sql(get_sql_query('user_events'))
    t_env.execute_sql(get_sql_query('checkout_events'))
    t_env.execute_sql(get_sql_query('user_profiles'))

    # Create Sink Tables
    t_env.execute_sql(get_sql_query('processed_events_kafka', 'sink'))
    t_env.execute_sql(get_sql_query('processed_events_postgres', 'sink'))

    # Run Processing Queries
    stmt_set = t_env.create_statement_set()
    stmt_set.add_insert_sql(get_sql_query('process_events_kafka', 'process'))
    stmt_set.add_insert_sql(get_sql_query('process_events_postgres', 'process'))
    
    processing_job = stmt_set.execute()
    print(
        f"""
        Async processing job started.
        Job status: {processing_job.get_job_client().get_job_status()}
        """
    )

if __name__ == '__main__':
    _, t_env_user = get_execution_environment(StreamJobConfig(job_name='user_event_processing_job'))
    run_user_event_processing_job(t_env_user)

    # Product Update Job
    _, t_env_product = get_execution_environment(StreamJobConfig(job_name='product_update_job'))
    run_product_update_job(t_env_product)
