import pandas as pd
import os.path as Path
from colorama import Fore, Style
from employee_attrition import params
import numpy as np
import unicodedata
from io import BytesIO

from google.cloud import bigquery
from google.cloud import storage


def get_data():
    '''
    Get the raw data from GCS or local and return cleaned data
    '''
    df_raw = pd.DataFrame()

    # Get Data from Goggle Cloud Storage
    if params.DATA_TARGET == 'gcs':
        # data_tuple = get_data_from_gcs()[1]
        # breakpoint()
        # data_events_ppl, data_scraped = data_tuple[0], data_tuple[1]
        print(Fore.BLUE + f"\nLoad latest data files from GCS..." + Style.RESET_ALL)

        bucket_name = params.BUCKET_NAME
        gsfile_path = f'gs://{bucket_name}/{params.RAW_DATA}'

        try:
            df_raw = pd.read_csv(gsfile_path)

            print("✅ Latest 2 files loaded from GCS")
        except Exception as e:
            print(f"Error in reading files from GCS, {e}")

    elif params.DATA_TARGET == 'local':
        print(Fore.BLUE + "\nLoad data from local CSV..." + Style.RESET_ALL)

        # Get Local Data
        if params.RAW_DATA is None:
            raise ValueError("RAW_DATA parameter is not set in params.")
        df_raw = pd.read_csv(Path.join("raw_data", params.RAW_DATA))

    else:
        print(Fore.RED + "\nMODEL_TARGET not set, exiting" + Style.RESET_ALL)
        return None

    # breakpoint()
    if len(df_raw) == 0:
        print(Fore.RED + "\nData is empty!" + Style.RESET_ALL)
        return None

    # Set EmployeeNumber as the index
    df_raw.set_index("EmployeeNumber", inplace=True)
    # Drop irrelevant columns
    df_raw.drop(columns=["EmployeeCount","StandardHours", "Over18"], inplace=True)
    # Create boolean target
    df_raw['Attrition'] = df_raw['Attrition'].map({'Yes': 1, 'No': 0})

    return df_raw

def load_data_to_bq(
        data: pd.DataFrame,
        gcp_project:str,
        bq_dataset:str,
        table: str,
        truncate: bool
    ) -> None:

    """
    - Save the DataFrame to BigQuery
    - Empty the table beforehand if `truncate` is True, append otherwise
    """
    pass



def save_data_to_gcs(
        cleaned_df: pd.DataFrame,
        feature_importance_df: pd.DataFrame,
        survival_df: pd.DataFrame
    ):

    '''
    Save the cleaned version of data in google cloud storage to make it available to Dashboard
    '''
    client = storage.Client()
    bucket = client.bucket(params.BUCKET_NAME)

    try:
        # Convert DataFrame to CSV format in memory
        cleaned_buffer_ml = BytesIO()
        cleaned_data.to_csv(cleaned_buffer_ml, index=False)


        # Specify the bucket name and CSV file path in GCS | Used in printing only
        # gcsfile_name_ml = f'gs://{params.BUCKET_NAME}/{params.CLEANED_FILE_ML}'
        # gcsfile_name_analytics = f'gs://{params.BUCKET_NAME}/{params.CLEANED_FILE_ANALYTICS}'

        # # Create a Blob object and upload the CSV data
        # blob_ml = bucket.blob(params.CLEANED_FILE_ML)
        # blob_ml.upload_from_string(csv_buffer_ml.getvalue(), content_type='text/csv')

        # blob_analysis = bucket.blob(params.CLEANED_FILE_ANALYTICS)
        # blob_analysis.upload_from_string(csv_buffer_analysis.getvalue(), content_type='text/csv')

    #     print(f"DataFrame successfully written to '{gcsfile_name_ml}'")
    #     print(f"DataFrame successfully written to '{gcsfile_name_analytics}'")

    #     return True, "OK"

    # except Exception as e:
    #     print(f"\n❌ No files saved in GCS bucket {bucket}")

    #     return False, e


def get_clean_data_from_gcs():
    '''
    This method will read the latest cleaned csv data from google cloud storage |
    '''
    print(Fore.BLUE + f"\nLoad latest cleaned data files needed for model from GCS..." + Style.RESET_ALL)

    bucket_name = params.BUCKET_NAME
    gsfile_clean_data_ml = f'gs://{bucket_name}/{params.CLEANED_FILE_ML}'

    try:
        data_ml = pd.read_csv(gsfile_clean_data_ml)
        print("✅ Latest clean ml file loaded from cloud storage")

        return (True, data_ml)
    except FileNotFoundError as e:
        print(f"\n❌ No clean ML file found in GCS bucket {bucket_name}")
        print(f"File {gsfile_clean_data_ml} not found in bucket {bucket_name}")
        return (False, e)
