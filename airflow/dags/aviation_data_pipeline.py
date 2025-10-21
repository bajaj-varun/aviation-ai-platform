from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeSqlApiOperator
from airflow.providers.snowflake.transfers.copy_into_snowflake import CopyFromExternalStageToSnowflakeOperator

# import sys, os
# sys.path.append('../config')
# sys.path.append('../plugins')

from aviation_operators import (
    ProcessAviationDocumentsOperator,
    UpdateVectorStoreOperator,
    DataQualityCheckOperator
)

from aviation_config import *

default_args = {
    'owner': 'aviation_ai',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'snowflake_conn_id': SNOWFLAKE_CONN_ID
}

with DAG(
    'aviation_data_pipeline',
    default_args=default_args,
    description='End-to-end aviation data processing pipeline',
    # schedule_interval='0 6 * * *',  # Daily at 6 AM
    catchup=False,
    tags=['aviation', 'etl', 'snowflake', 'vector_store']
) as dag:

    # Start Pipeline
    start_pipeline = PythonOperator(
        task_id='start_pipeline',
        python_callable=lambda: print("Starting Aviation Data Pipeline")
    )

    # Extract flight data from source systems
    extract_flight_data = SnowflakeSqlApiOperator(
        task_id='extract_flight_data',
        sql='''
        INSERT INTO {{ params.target_table }}
        SELECT 
            flight_number,
            airline_code,
            departure_airport,
            arrival_airport,
            scheduled_departure,
            scheduled_arrival,
            status,
            aircraft_type,
            distance_km,
            CURRENT_TIMESTAMP() as loaded_at
        FROM staging.flights_raw
        WHERE DATE(scheduled_departure) = CURRENT_DATE()
        ''',
        params={'target_table': 'flights'}
    )

    # Extract cargo manifests
    extract_cargo_data = SnowflakeSqlApiOperator(
        task_id='extract_cargo_data',
        sql='''
        INSERT INTO {{ params.target_table }}
        SELECT 
            flight_number,
            waybill_number,
            shipper_name,
            consignee_name,
            cargo_description,
            weight_kg,
            volume_cubic_m,
            special_handling,
            hazardous_material,
            hazmat_class,
            CURRENT_TIMESTAMP() as loaded_at
        FROM staging.cargo_raw
        WHERE DATE(created_at) = CURRENT_DATE()
        ''',
        params={'target_table': 'cargo_manifests'}
    )

    # Load data from S3 (if you have external data sources)
    load_external_data = CopyFromExternalStageToSnowflakeOperator(
        task_id='load_external_data',
        # s3_keys=['s3://aviation-data/external/flights_{{ ds_nodash }}.csv'],
        table='staging.external_flights',
        schema=SNOWFLAKE_SCHEMA,
        stage='aviation_stage',
        file_format='(TYPE = CSV, SKIP_HEADER = 1)'
    )

    # Process aviation documents for vector store
    process_aviation_documents = ProcessAviationDocumentsOperator(
        task_id='process_aviation_documents',
        document_paths=DATA_SOURCES['aviation_docs']['paths'],
        mongodb_conn_id=MONGODB_CONN_ID,
        aws_conn_id=AWS_CONN_ID
    )

    # Update vector store with new documents
    update_vector_store = UpdateVectorStoreOperator(
        task_id='update_vector_store',
        message="update_vector_store",
        mongodb_conn_id=MONGODB_CONN_ID,
        aws_conn_id=AWS_CONN_ID,
        collection_name=MONGODB_COLLECTION
    )

    # Data quality checks
    data_quality_flights = DataQualityCheckOperator(
        task_id='data_quality_flights',
        table_name='flights',
        checks=[
            {'check_sql': 'SELECT COUNT(*) FROM flights WHERE flight_number IS NULL', 'expected_result': 0},
            {'check_sql': 'SELECT COUNT(*) FROM flights WHERE scheduled_departure > scheduled_arrival', 'expected_result': 0}
        ]
    )

    data_quality_cargo = DataQualityCheckOperator(
        task_id='data_quality_cargo',
        table_name='cargo_manifests',
        checks=[
            {'check_sql': 'SELECT COUNT(*) FROM cargo_manifests WHERE weight_kg <= 0', 'expected_result': 0},
            {'check_sql': 'SELECT COUNT(*) FROM cargo_manifests WHERE flight_number IS NULL', 'expected_result': 0}
        ]
    )

    # Generate daily reports
    generate_daily_report = SnowflakeSqlApiOperator(
        task_id='generate_daily_report',
        sql='''
        CREATE OR REPLACE TABLE daily_operations_report AS
        SELECT 
            f.flight_number,
            f.airline_code,
            f.departure_airport,
            f.arrival_airport,
            f.status,
            COUNT(cm.waybill_number) as total_shipments,
            SUM(cm.weight_kg) as total_cargo_weight,
            SUM(CASE WHEN cm.hazardous_material THEN 1 ELSE 0 END) as hazardous_shipments
        FROM flights f
        LEFT JOIN cargo_manifests cm ON f.flight_number = cm.flight_number
        WHERE DATE(f.scheduled_departure) = CURRENT_DATE()
        GROUP BY f.flight_number, f.airline_code, f.departure_airport, f.arrival_airport, f.status
        '''
    )

    # End Pipeline
    end_pipeline = PythonOperator(
        task_id='end_pipeline',
        python_callable=lambda: print("Aviation Data Pipeline completed successfully")
    )

    # Define dependencies
    start_pipeline >> [extract_flight_data, extract_cargo_data, load_external_data]
    
    extract_flight_data >> data_quality_flights
    extract_cargo_data >> data_quality_cargo
    load_external_data >> process_aviation_documents
    
    [data_quality_flights, data_quality_cargo] >> generate_daily_report
    process_aviation_documents >> update_vector_store
    
    [generate_daily_report, update_vector_store] >> end_pipeline