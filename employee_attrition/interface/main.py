import pandas as pd
import numpy as np
import os.path as Path

from colorama import Fore, Style

from employee_attrition.ml_logic.data import get_data, save_data, get_processed_data
from employee_attrition.ml_logic.registry import load_model, save_model
from employee_attrition.ml_logic.model import train_model
from employee_attrition import params

# Split into structured target for survival analysis and features
from sksurv.util import Surv


def train(save=True):
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

    print(Fore.BLUE + "\n Training the model.." + Style.RESET_ALL)
    pipeline = train_model(X,y)

    # Extract feature importances from the model
    feature_importances = pipeline.named_steps['model'].feature_importances_
    preprocessor = pipeline.named_steps['preprocessor']
    transformed_feature_names = preprocessor.get_feature_names_out()
    # Sort and plot feature importance
    feature_importance_df = pd.DataFrame({'Feature': transformed_feature_names, 'Importance': feature_importances})
    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

    # Filter df to include only employees who haven't quit (Attrition == 0)
    active_df = raw_data[raw_data['Attrition'] == 0]
    risk_score_df = active_df.drop(columns=['Attrition', 'YearsAtCompany'])
    # Add the predicted risk scores to the DataFrame
    risk_score_df['PredictedRisk'] = pipeline.predict(risk_score_df)
    # Get back the YearsAtCompany for the employees who haven't quit
    risk_score_df['YearsAtCompany'] = active_df['YearsAtCompany']

    # Sort by predicted risk (highest risk first)
    risk_score_df = risk_score_df.sort_values(by='PredictedRisk', ascending=False)

    # Save model and data
    if save == True:
        save_model(pipeline)
        save_data(raw_data, feature_importance_df, risk_score_df)



def train_model_with_selection(save=False):

    pass

def evaluate():
    pass

def predict_curves_on_data(pipeline, risk_scores_df,num_samples=None, max_time=10):
    if num_samples is None or num_samples > len(risk_scores_df):
        num_samples = len(risk_scores_df)
    top_n_high_risk = risk_scores_df.head(num_samples) # type: ignore
    print(top_n_high_risk[['PredictedRisk']])

    # Preprocess the top high-risk employees' data
    top_n_high_risk_proc = pipeline.named_steps['preprocessor'].transform(top_n_high_risk.drop(columns=['PredictedRisk']))
    top_n_high_risk_proc = pipeline.named_steps['to_dataframe'].transform(top_n_high_risk_proc)
    survival_funcs = pipeline.named_steps['model'].predict_survival_function(top_n_high_risk_proc)

    # Create a DataFrame to store survival probabilities for the top n high-risk employees
    survival_data = []
    # Extract time points and survival probabilities from the survival functions (StepFunction)
    for i, employee_id in enumerate(top_n_high_risk.index):
        step_function = survival_funcs[i]  # Get the StepFunction for the current employee
        time_points = step_function.x  # Time points
        survival_prob = step_function.y  # Survival probabilities

        # Add the survival curve to the DataFrame
        for time, prob in zip(time_points, survival_prob):
            survival_data.append({
                'EmployeeNumber': employee_id,
                'Time': time,
                'SurvivalProbability': prob
            })

    # Convert the survival data to a DataFrame
    survival_df = pd.DataFrame(survival_data)
    return top_n_high_risk_proc, survival_df

def predict_risk(num_samples=10, max_time=10):

    '''
    Get survival curves for the top n high-risk employees
    '''
    pipeline = load_model()
    if pipeline is None:
        raise ValueError("Failed to load model. Please check the model source or `load_model()` function.")

    data_loaded, raw_data, feature_importance_df, risk_scores_df = get_processed_data() # type: ignore

    if not data_loaded:
        raise ValueError("Failed to load processed data. Please check the data source or `get_processed_data()` function.")

    print(Fore.BLUE + "\n Data successfully loaded for prediction." + Style.RESET_ALL)

    return predict_curves_on_data(pipeline, risk_scores_df, num_samples, max_time)


if __name__ == '__main__':
    train()
    # train_model2(save=True)
    evaluate()
    predict_risk()
