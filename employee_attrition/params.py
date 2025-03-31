import os
import numpy as np

MODEL_TARGET = os.environ.get("MODEL_TARGET")
DATA_TARGET = os.environ.get("DATA_TARGET")
DATA_SOURCE = os.environ.get("DATA_SOURCE")

##################  GCP VARIABLES  ##################
GCP_PROJECT = os.environ.get("GCP_PROJECT")
GCP_REGION = os.environ.get("GCP_REGION")

BQ_DATASET = os.environ.get("BQ_DATASET")
BQ_REGION = os.environ.get("BQ_REGION")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
INSTANCE = os.environ.get("INSTANCE")


##################  DATA FILES  ##################
RAW_DATA = os.environ.get("RAW_DATA")
CLEANED_DATA = os.environ.get("CLEANED_DATA")
FEATURE_IMPORTANCE_DATA = os.environ.get("FEATURE_IMPORTANCE_DATA")
RISK_SCORE_DATA = os.environ.get("RISK_SCORE_DATA")


##################  MODEL LIFECYCLE  #####################

MLFLOW_TRACKING_URI='https://mlflow.lewagon.ai'
MLFLOW_EXPERIMENT='employee_attrition_experiment'
MLFLOW_MODEL_NAME='employee_attrition_pipe'
PREFECT_FLOW_NAME = os.environ.get("PREFECT_FLOW_NAME")
PREFECT_LOG_LEVEL = os.environ.get("PREFECT_LOG_LEVEL")
GAR_IMAGE = os.environ.get("GAR_IMAGE")
GAR_MEMORY = os.environ.get("GAR_MEMORY")


LOCAL_CACHE_DIR  = os.environ.get("LOCAL_CACHE_DIR")
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
