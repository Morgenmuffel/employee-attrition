import pandas as pd
import numpy as np
import os.path as Path

from colorama import Fore, Style

from employee_attrition.ml_logic.data import get_data, save_data_to_gcs
from employee_attrition.ml_logic.registry import load_model, save_model
from employee_attrition.ml_logic.model import train_model
from employee_attrition import params

# Split into structured target for survival analysis and features
from sksurv.util import Surv


def train(save=False):
    """
    - Get the raw data
    - Train the Survival Analysis model on the preprocessed dataset
    - Save the pipeline and metrics
    - Save data for further analysis and dashboard
    """
    print(Fore.MAGENTA + "\n⭐️ Use case: train" + Style.RESET_ALL)


    raw_data = get_data()
    if raw_data is None:
        raise ValueError("Failed to load raw data. Please check the data source or `get_data()` function.")

    # Split into structured target for survival analysis and features
    X = raw_data.drop(columns=['Attrition', 'YearsAtCompany'])
    y = Surv.from_arrays(event=raw_data["Attrition"] == 1, time=raw_data["YearsAtCompany"])
    # Train model using `model.py`
    pipeline = load_model()

    if pipeline is None:
        print(Fore.BLUE + "\n Training the model.." + Style.RESET_ALL)
        pipeline = train_model(X,y)

        # Save model
        if save == True:
            save_model(pipeline)
            # Save resuts
            # Saving the clusters returned by the model in the original raw ml_data
            save_results(raw_ml_data, model.labels_)


def train_model_with_selection(save=False):

    pass

def evaluate():
    pass

def pred():

    '''
    Predicting the probability of attending the event for a new/existing user
    '''
    X_pred = pd.read_csv("raw_data/predict.csv")
    preproc_pipeline = load_preproc_pipeline()

    # Commented | As we commented preprocess_features in preprocess method
    # if preproc_pipeline == None:
    #     print(Fore.BLUE + "\n Failed to load preproc pipeline \n Preprocessing the raw data.." + Style.RESET_ALL)
    #     X_processed, y_train = preprocess()
    #     preproc_pipeline = load_preproc_pipeline()

    X_pred_process = preproc_pipeline.transform(X_pred)

    # Train model using `model.py`
    model = load_model()

    # Predict probability of a person to attend
    probabilities = model.predict_proba(X_pred_process)

    # Get probability of positive result (class 1)
    positive_probabilities = probabilities[:, 1]

    print(positive_probabilities)


if __name__ == '__main__':
    train()
    # train_model2(save=True)
    evaluate()
    pred()
