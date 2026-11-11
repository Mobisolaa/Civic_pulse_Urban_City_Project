from airflow import DAG
from datetime import datetime, timedelta
from airflow.sdk import task

from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.microsoft.azure.operators.data_factory import AzureDataFactoryRunPipelineOperator

from include.transform import transform
from include.upload import upload_data ##function defined in the upload.py with the blob service account

default_args = {
    'owner': 'amdari',
    'depends_on_past': False, ## if set to True, the task instance will not run if the previous task instance has failed. If set to False, the task instance will run regardless of the previous task instance's state.
    'start_date' : datetime(2026,11,7),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
   
    'azure_data_factory_conn_id': 'azure_factory',##connection id defined in the airflow connections. This is used to connect to the Azure Data Factory.
     'factory_name': 'ucp-factory',
     'resource_group_name':'Service_Request'
}

##DAG is a collection of tasks that are organized in a way that reflects their relationships and dependencies.
@task()
def extract_data_from_api():
    api_response = upload_data() ##function defined in the upload.py with the blob service account
    return api_response

@task()
def transform_data():
    cleaned_data = transform()
    return cleaned_data

with DAG(dag_id='urban_city_requests',
    catchup = False, default_args= default_args, schedule='@daily') as dag:

    create_db_table = SQLExecuteQueryOperator(
        sql = 'sql/urban_city.sql',
        task_id = 'urban_city_table',
        conn_id = 'postgres_conn'

    )
    data_factory = AzureDataFactoryRunPipelineOperator(
        task_id = 'run_data_factory',
        pipeline_name ='UrdanCityDataFactoryPipeline' ##name of the pipeline in Azure Data Factory (i spelt it wrongly in ADF)
    )

    #The >> operator is used to set the order of execution of tasks in the DAG. extract_data will run before transform_data
    extract_data_from_api() >> transform_data() >> create_db_table >> data_factory
