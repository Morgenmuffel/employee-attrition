import os

import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from prefect import task, flow

from employee_attrition.interface.main import evaluate, preprocess, train
from employee_attrition.ml_logic.registry import mlflow_transition_model
from employee_attrition.params import *

@task
def preprocess_new_data(min_date: str, max_date: str):
    return preprocess(min_date=min_date, max_date=max_date)

@task
def evaluate_production_model(min_date: str, max_date: str):
    return evaluate(min_date=min_date, max_date=max_date)

@task
def re_train(min_date: str, max_date: str, split_ratio: str):
    return train(min_date=min_date, max_date=max_date, split_ratio=split_ratio)

@task
def transition_model(current_stage: str, new_stage: str):
    return mlflow_transition_model(current_stage=current_stage, new_stage=new_stage)




@flow(name=PREFECT_FLOW_NAME)
def train_flow():
    """
    Build the Prefect workflow for the `taxifare` package. It should:
        - preprocess 1 month of new data, starting from EVALUATION_START_DATE
        - compute `old_mae` by evaluating the current production model in this new month period
        - compute `new_mae` by re-training, then evaluating the current production model on this new month period
        - if the new one is better than the old one, replace the current production model with the new one
        - if neither model is good enough, send a notification!
    """

    min_date = EVALUATION_START_DATE
    max_date = str(datetime.strptime(min_date, "%Y-%m-%d") + relativedelta(months=1)).split()[0]

    preprocessed = preprocess_new_data.submit(min_date=min_date, max_date=max_date)

    old_mae = evaluate_production_model.submit(min_date=min_date, max_date=max_date, wait_for=[preprocessed])
    new_mae = re_train.submit(min_date=min_date, max_date=max_date, split_ratio = 0.2, wait_for=[preprocessed])

    old_mae = old_mae.result()
    new_mae = new_mae.result()

    if new_mae < old_mae:
        print(f"🚀 New model replacing old in production with MAE: {new_mae} the Old MAE was: {old_mae}")
        transition_model.submit(current_stage="Staging", new_stage="Production")
    else:
        print(f"🚀 Old model kept in place with MAE: {old_mae}. The new MAE was: {new_mae}")

    notify.submit(old_mae, new_mae)

if __name__ == "__main__":
    train_flow()
