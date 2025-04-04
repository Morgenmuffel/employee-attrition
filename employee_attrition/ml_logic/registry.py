import glob
import os
import time
import pickle

from colorama import Fore, Style
from google.cloud import storage
from sklearn.pipeline import Pipeline

from employee_attrition.params import *
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

# def save_results(params: dict, metrics: dict) -> None:
#     """
#     Persist params & metrics locally on the hard drive at
#     "{LOCAL_REGISTRY_PATH}/params/{current_timestamp}.pickle"
#     "{LOCAL_REGISTRY_PATH}/metrics/{current_timestamp}.pickle"
#     -  if MODEL_TARGET='mlflow', also persist them on MLflow
#     """
#     if MODEL_TARGET == "mlflow":
#         if params is not None:
#             mlflow.log_params(params)
#         if metrics is not None:
#             mlflow.log_metrics(metrics)
#         print("✅ Results saved on MLflow")

#     timestamp = time.strftime("%Y%m%d-%H%M%S")

#     # Save params locally
#     if params is not None:
#         params_path = os.path.join(LOCAL_REGISTRY_PATH, "params", timestamp + ".pickle")
#         with open(params_path, "wb") as file:
#             pickle.dump(params, file)

#     # Save metrics locally
#     if metrics is not None:
#         metrics_path = os.path.join(LOCAL_REGISTRY_PATH, "metrics", timestamp + ".pickle")
#         with open(metrics_path, "wb") as file:
#             pickle.dump(metrics, file)

#     print("✅ Results saved locally")


from typing import Optional

def save_model(pipeline: Optional[Pipeline] = None) -> None:
    """
    Persist trained model locally on the hard drive at f"{LOCAL_REGISTRY_PATH}/models/{timestamp}.pkl"
    - if MODEL_TARGET='gcs', also persist it in your bucket on GCS at "models/{timestamp}.pkl"
    - if MODEL_TARGET='mlflow', also persist it on MLflow instead of GCS
    """

    timestamp = time.strftime("%Y%m%d-%H%M%S")

    # Save model locally
    model_path = os.path.join(LOCAL_REGISTRY_PATH, "models")
    model_filename = f"{timestamp}.pkl"
    full_model_path = os.path.join(model_path, model_filename)

    if not os.path.exists(model_path):
        os.makedirs(model_path)

    with open(full_model_path, 'wb') as f:
        pickle.dump(pipeline, f)
        print("✅ Model saved locally")

    if MODEL_TARGET == "gcs":
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"models/{model_filename}")
        blob.upload_from_filename(full_model_path)

        print("✅ Model saved to GCS")

        return None

    if MODEL_TARGET == "mlflow":
        mlflow.sklearn.log_model(
            sk_model=pipeline,  # Sklearn model
            artifact_path="model",  # Artifact path within the run
            registered_model_name=MLFLOW_MODEL_NAME,  # Registered model name
        )

        print("✅ Model saved to MLflow")

        return None

    return None


def load_model(stage="Production"):
    """
    Return a saved model:
    - locally (latest one in alphabetical order)
    - or from GCS (most recent one) if MODEL_TARGET=='gcs'  --> for unit 02 only
    - or from MLFLOW (by "stage") if MODEL_TARGET=='mlflow' --> for unit 03 only

    Return None (but do not Raise) if no model is found

    """

    if MODEL_TARGET == "local":
        print(Fore.BLUE + f"\nLoad latest model from local registry..." + Style.RESET_ALL)

        # Get the latest model version name by the timestamp on disk
        local_model_directory = os.path.join(LOCAL_REGISTRY_PATH, "models")
        local_model_paths = glob.glob(f"{local_model_directory}/*")

        if not local_model_paths:
            return None

        most_recent_model_path_on_disk = sorted(local_model_paths)[-1]

        print(Fore.BLUE + f"\nLoad latest model from disk..." + Style.RESET_ALL)

        # Load model from disk using pickle
        with open(most_recent_model_path_on_disk, 'rb') as f:
            latest_model = pickle.load(f)

        print("✅ Model loaded from local disk")

        return latest_model

    # elif MODEL_TARGET == "gcs":

    #     print(Fore.BLUE + f"\nLoad latest model from GCS..." + Style.RESET_ALL)

    #     client = storage.Client()
    #     blobs = list(client.get_bucket(BUCKET_NAME).list_blobs(prefix="model"))

    #     try:
    #         latest_blob = max(blobs, key=lambda x: x.updated)
    #         latest_model_path_to_save = os.path.join(LOCAL_REGISTRY_PATH, latest_blob.name)
    #         latest_blob.download_to_filename(latest_model_path_to_save)

    #         latest_model = keras.models.load_model(latest_model_path_to_save)

    #         print("✅ Latest model downloaded from cloud storage")

    #         return latest_model
    #     except:
    #         print(f"\n❌ No model found in GCS bucket {BUCKET_NAME}")

    #         return None

    elif MODEL_TARGET == "mlflow":
        print(Fore.BLUE + f"\nLoad [{stage}] model from MLflow..." + Style.RESET_ALL)

        # Load model from MLflow
        model = None
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI) # type: ignore
        client = MlflowClient()

        try:
            model_versions = client.get_latest_versions(name=MLFLOW_MODEL_NAME, stages=[stage])
            model_uri = model_versions[0].source

            assert model_uri is not None
        except:
            print(f"\n❌ No model found with name {MLFLOW_MODEL_NAME} in stage {stage}")

            return None

        model = mlflow.sklearn.load_model(model_uri)

        print("✅ Model loaded from MLflow")
        return model
    else:
        return None



def mlflow_transition_model(current_stage: str, new_stage: str) -> None:
    """
    Transition the latest model from the `current_stage` to the
    `new_stage` and archive the existing model in `new_stage`
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI) # type: ignore

    client = MlflowClient()

    version = client.get_latest_versions(name=MLFLOW_MODEL_NAME, stages=[current_stage])

    if not version:
        print(f"\n❌ No model found with name {MLFLOW_MODEL_NAME} in stage {current_stage}")
        return None

    client.transition_model_version_stage(
        name=MLFLOW_MODEL_NAME,
        version=version[0].version,
        stage=new_stage,
        archive_existing_versions=True
    )

    print(f"✅ Model {MLFLOW_MODEL_NAME} (version {version[0].version}) transitioned from {current_stage} to {new_stage}")

    return None


# def mlflow_run(func):
#     """
#     Generic function to log params and results to MLflow along with TensorFlow auto-logging

#     Args:
#         - func (function): Function you want to run within the MLflow run
#         - params (dict, optional): Params to add to the run in MLflow. Defaults to None.
#         - context (str, optional): Param describing the context of the run. Defaults to "Train".
#     """
#     def wrapper(*args, **kwargs):
#         mlflow.end_run()
#         mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
#         mlflow.set_experiment(experiment_name=MLFLOW_EXPERIMENT)

#         with mlflow.start_run():
#             mlflow.autolog()
#             results = func(*args, **kwargs)

#         print("✅ mlflow_run auto-log done")

#         return results
#     return wrapper
