import polars as pl ##polars is a fast dataframe library, similar to pandas but faster and more efficient for large datasets
import os
from importlib import import_module
load_dotenv = import_module("dotenv").load_dotenv
load_dotenv()

storage_options = {
    "account_name": "civicpulseucp",
    "account_key": os.getenv('UCP_STORAGE_KEY')
}
def transform():
    source_uri = 'az://bronze-ucp/urban_service_requests.csv'
    target_uri = 'az://silver-ucp/urban_service_requests_transformed.csv'
    df = pl.scan_csv(source_uri, storage_options=storage_options) ##if it were pandas,it would be pd.read_csv(source_uri, storage_options=storage_options)

    ##clean up column headers, replace spaces with underscores and convert to lowercase
    df = df.rename({col:
                     col.strip()
                     .replace(' ', '_').lower()
                     .replace('(','_').lower()
                     .replace(')','_').lower()
                       for col in df.columns})
    df.sink_parquet(target_uri, storage_options=storage_options, compression='snappy')
    print(f'data loaded to silver layer at {target_uri}')
    return None

transform()