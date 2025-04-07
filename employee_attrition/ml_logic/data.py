import pandas as pd
import os.path as Path
from colorama import Fore, Style
from employee_attrition import params
from io import BytesIO

from google.cloud import bigquery
from google.cloud import storage



def get_data():
    '''
    Get the raw data from GCS or local and return cleaned data
    '''
    df_raw = pd.DataFrame()

    # Get Data from Goggle Cloud Storage
    if params.DATA_SOURCE == 'gcs':
        # data_tuple = get_data_from_gcs()[1]
        # breakpoint()

        print(Fore.BLUE + f"\nLoad latest data files from GCS..." + Style.RESET_ALL)

        bucket_name = params.BUCKET_NAME
        gsfile_path = f'gs://{bucket_name}/{params.RAW_DATA}'

        try:
            df_raw = pd.read_csv(gsfile_path)

            print("✅ Latest 2 files loaded from GCS")
        except Exception as e:
            print(f"Error in reading files from GCS, {e}")

    elif params.DATA_SOURCE == 'local':
        print(Fore.BLUE + "\nLoad data from local CSV..." + Style.RESET_ALL)

        # Get Local Data
        if params.RAW_DATA is None or params.LOCAL_CACHE_DIR is None:
            raise ValueError("LOCAL_CACHE_DIR/RAW_DATA parameter is not set in params.")
        df_raw = pd.read_csv(Path.join(params.LOCAL_CACHE_DIR,params.RAW_DATA))

    else:
        print(Fore.RED + "\nDATA_TARGET not set, exiting" + Style.RESET_ALL)
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

def save_data(
        cleaned_df: pd.DataFrame,
        feature_importance_df: pd.DataFrame,
        risk_score_df: pd.DataFrame
    ):

    '''
    Save the processed version of data in DATA_TARGET
    '''
    if params.DATA_TARGET == 'local':
        print(Fore.BLUE + "\n Saving processed data locally.." + Style.RESET_ALL)
        cleaned_df.to_csv(f'raw_data/{params.CLEANED_DATA}', index=True)
        feature_importance_df.to_csv(f'raw_data/{params.FEATURE_IMPORTANCE_DATA}')
        risk_score_df.to_csv(f'raw_data/{params.RISK_SCORE_DATA}', index=True)
    elif params.DATA_TARGET == 'gcs':
        print(Fore.BLUE + "\n Saving processed data to the gcs.." + Style.RESET_ALL)
        save_data_to_gcs(cleaned_df,  feature_importance_df, risk_score_df)

def save_data_to_gcs(
        cleaned_df: pd.DataFrame,
        feature_importance_df: pd.DataFrame,
        risk_score_df: pd.DataFrame
    ):

    '''
    Save the processed version of data in google cloud storage to make it available to Dashboard
    '''
    client = storage.Client()
    bucket = client.bucket(params.BUCKET_NAME)

    try:
        # Convert DataFrame to CSV format in memory
        cleaned_data_buffer = BytesIO()
        cleaned_df.columns = cleaned_df.columns.str.strip().str.replace(r'[\n\r]', '', regex=True)
        cleaned_df.to_csv(cleaned_data_buffer, index=True)

        feature_importance_buffer = BytesIO()
        feature_importance_df.columns = feature_importance_df.columns.str.strip().str.replace(r'[\n\r]', '', regex=True)
        feature_importance_df.to_csv(feature_importance_buffer)

        survival_data_buffer = BytesIO()
        risk_score_df.columns = risk_score_df.columns.str.strip().str.replace(r'[\n\r]', '', regex=True)
        risk_score_df.to_csv(survival_data_buffer, index=True)


        # Specify the bucket name and CSV file path in GCS | Used in printing only
        gcsfile_name_cleaned = f'gs://{params.BUCKET_NAME}/{params.CLEANED_DATA}'
        gcsfile_name_feature_imp = f'gs://{params.BUCKET_NAME}/{params.FEATURE_IMPORTANCE_DATA}'
        gcsfile_name_survival = f'gs://{params.BUCKET_NAME}/{params.RISK_SCORE_DATA}'

        # Create a Blob object and upload the CSV data
        blob_cleaned = bucket.blob(params.CLEANED_DATA)
        blob_cleaned.upload_from_string(cleaned_data_buffer.getvalue(), content_type='text/csv')

        blob_feature_imp = bucket.blob(params.FEATURE_IMPORTANCE_DATA)
        blob_feature_imp.upload_from_string(feature_importance_buffer.getvalue(), content_type='text/csv')

        blob_survival = bucket.blob(params.RISK_SCORE_DATA)
        blob_survival.upload_from_string(survival_data_buffer.getvalue(), content_type='text/csv')

        print(f"cleaned_df successfully written to '{gcsfile_name_cleaned}'")
        print(f"feature_importance_df successfully written to '{gcsfile_name_feature_imp}'")
        print(f"survival_df successfully written to '{gcsfile_name_survival}'")

        return True, "OK"

    except Exception as e:
        print(f"\n❌ No files saved in GCS bucket {bucket}")
        return False, e




def get_processed_data_from_gcs():
    '''
    Retrieve the processed data from Google Cloud Storage and return as DataFrames

    Returns:
        tuple: (success_status, cleaned_df, feature_importance_df, risk_score_df)
               success_status is True if all data was retrieved successfully
    '''
    client = storage.Client()
    bucket = client.bucket(params.BUCKET_NAME)

    try:
        # Get cleaned data
        blob_cleaned = bucket.blob(params.CLEANED_DATA)
        cleaned_data = blob_cleaned.download_as_string()
        cleaned_df = pd.read_csv(BytesIO(cleaned_data), index_col='EmployeeNumber')

        # Get feature importance data
        blob_feature_imp = bucket.blob(params.FEATURE_IMPORTANCE_DATA)
        feature_imp_data = blob_feature_imp.download_as_string()
        feature_importance_df = pd.read_csv(BytesIO(feature_imp_data))

        # Get risk score data
        blob_survival = bucket.blob(params.RISK_SCORE_DATA)
        risk_score_data = blob_survival.download_as_string()
        risk_score_df = pd.read_csv(BytesIO(risk_score_data), index_col='EmployeeNumber')

        print("Successfully retrieved all data from GCS")
        return True, cleaned_df, feature_importance_df, risk_score_df

    except Exception as e:
        print(f"Error retrieving data from GCS: {e}")
        return False, None, None, None

def get_processed_data():
    '''
    Get processed data, first trying local cache, then falling back to GCS

    Returns:
        tuple: (cleaned_df, feature_importance_df, risk_score_df) if successful
        None: if unsuccessful
    '''
    data_loaded = False
    cleaned_df = None
    feature_importance_df = None
    risk_score_df = None


    if params.DATA_TARGET == 'local':

        if params.LOCAL_CACHE_DIR is None:
            raise ValueError("/RAW_DATA parameter is not set in params.")


        print(Fore.RED + "\nLoad processed data from local cache " + params.LOCAL_CACHE_DIR + Style.RESET_ALL)
        # Ensure cache directory exists
        if not Path.exists(params.LOCAL_CACHE_DIR):
            raise ValueError("Cache directory does not exist.")
        else:
            try:
                # Define local file paths
                local_cleaned_path = Path.join(params.LOCAL_CACHE_DIR, params.CLEANED_DATA) # type: ignore
                local_feature_imp_path = Path.join(params.LOCAL_CACHE_DIR, params.FEATURE_IMPORTANCE_DATA) # type: ignore
                local_risk_score_path = Path.join(params.LOCAL_CACHE_DIR, params.RISK_SCORE_DATA) # type: ignore

                # Check if all files exist
                if (Path.exists(local_cleaned_path) and \
                    Path.exists(local_feature_imp_path) and \
                    Path.exists(local_risk_score_path)):

                    cleaned_df = pd.read_csv(local_cleaned_path, index_col='EmployeeNumber')
                    feature_importance_df = pd.read_csv(local_feature_imp_path)
                    risk_score_df = pd.read_csv(local_risk_score_path, index_col='EmployeeNumber')
                    data_loaded = True
                    print("✅ Successfully loaded all data from local cache")

            except Exception as e:
                print(f"⚠️ Error reading local cache files: {e}")
                raise ValueError("Error reading local cache files")

        return data_loaded, cleaned_df, feature_importance_df, risk_score_df

    elif params.DATA_TARGET == 'gcs':
        return get_processed_data_from_gcs()
