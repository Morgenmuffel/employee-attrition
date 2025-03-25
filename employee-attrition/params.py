import os
import numpy as np

MODEL_TARGET = os.environ.get("MODEL_TARGET")
DATA_TARGET = os.environ.get("DATA_TARGET")

##################  GCP VARIABLES  ##################
GCP_PROJECT = os.environ.get("GCP_PROJECT")
GCP_REGION = os.environ.get("GCP_REGION")

BQ_DATASET = os.environ.get("BQ_DATASET")
BQ_REGION = os.environ.get("BQ_REGION")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
RAW_DATA = os.environ.get("RAW_DATA")
CLEANED_DATA_ML = os.environ.get("CLEANED_FILE_ML")
CLEANED_DATA_ANALYTICS = os.environ.get("CLEANED_FILE_ANALYTICS")
INSTANCE = os.environ.get("INSTANCE")

# MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI")
# MLFLOW_EXPERIMENT = os.environ.get("MLFLOW_EXPERIMENT")
# MLFLOW_MODEL_NAME = os.environ.get("MLFLOW_MODEL_NAME")
# Model Lifecycle
MLFLOW_TRACKING_URI='https://mlflow.lewagon.ai'
MLFLOW_EXPERIMENT='employee_attrition_experiment_sydd'
MLFLOW_MODEL_NAME='employee_attrition_experiment_sydd'

##################  CONSTANTS  #####################

# LOCAL_DATA_PATH = os.path.join(os.path.curdir(), "raw_data")
# LOCAL_REGISTRY_PATH = os.path.join(os.path.dirname(__file__), ".lewagon", "employee_attrition", "training_outputs")
# LOCAL_REGISTRY_PATH = os.path.join(os.path.expanduser('~'), ".lewagon", "employee_attrition", "training_outputs")
# LOCAL_REGISTRY_PATH = os.path.join(PROJECT_ROOT, ".lewagon", "employee_attrition", "training_outputs")

# LOCAL_REGISTRY_PATH =  '~/.lewagon/employee_attrition'
# LOCAL_REGISTRY_PATH =  '/home/yuliav/.lewagon/employee_attrition'


# IS_DOCKER = os.environ.get('DOCKER_ENV', False)

##################  CONSTANTS  #####################
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOCAL_REGISTRY_PATH = os.path.join(PROJECT_ROOT, "training_outputs")
