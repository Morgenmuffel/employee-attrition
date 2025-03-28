
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from colorama import Fore, Style
import pandas as pd

from employee_attrition.ml_logic.data import load_data_to_bq
from employee_attrition.params import *

from sksurv.ensemble import GradientBoostingSurvivalAnalysis
from sksurv.metrics import concordance_index_censored



# **Create a Custom Transformer to Convert Output to DataFrame**
# Need it for GradientBoostingSurvivalAnalysis to retain feature names
class ToDataFrame(BaseEstimator, TransformerMixin):
    def __init__(self, preprocessor):
        """
        Initialize the transformer with a fitted preprocessor.
        :param preprocessor: A fitted ColumnTransformer or similar preprocessor.
        """
        self.preprocessor = preprocessor
        self.feature_names = None

    def fit(self, X, y=None):
        """
        Fit the transformer (no-op since the preprocessor is already fitted).
        """
        # Extract feature names from the fitted preprocessor
        self.feature_names = self.preprocessor.get_feature_names_out()
        return self

    def transform(self, X):
        """
        Transform the input data into a DataFrame with feature names.
        :param X: Input data (NumPy array or similar).
        :return: Pandas DataFrame with feature names.
        """
        return pd.DataFrame(X, columns=self.feature_names)

def train_model(
        X : pd.DataFrame,
        y: np.ndarray,
       # validation_data=None, # overrides validation_split
        model = None,
        validation_split=0.2
    ) :

    """
    1. Get the pre-processed data from the pipeline
    2. Implement the model
    3. Return the model   """

    # Define numerical and categorical features
    numerical_columns = ['Age', 'DailyRate', 'MonthlyRate','DistanceFromHome', 'HourlyRate', 'JobInvolvement',
                        'JobLevel', 'MonthlyIncome', 'NumCompaniesWorked', 'PercentSalaryHike',
                        'PerformanceRating','TotalWorkingYears',
                        'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsInCurrentRole',
                        'YearsSinceLastPromotion', 'YearsWithCurrManager']

    categorical_columns = ['Gender', 'BusinessTravel', 'Department', 'EducationField', 'JobRole',
                        'MaritalStatus', 'OverTime']

    # Create column transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_columns),
            ('cat', OneHotEncoder(), categorical_columns)
        ],
        verbose_feature_names_out = False,
        remainder='passthrough'
    )

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=validation_split
    )
    # Define the model
    model = GradientBoostingSurvivalAnalysis(n_estimators=100, learning_rate=0.1)

    # Create the pipeline with the custom transformer
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('to_dataframe', ToDataFrame(preprocessor=preprocessor)),  # Pass the preprocessor
        ('model', model)
    ])
    # Fit the model
    pipeline.fit(X_train, y_train)

    # Predict risk scores (higher = more likely to leave sooner)
    predicted_risk = pipeline.predict(X_test)
    # Calculate concordance index
    c_index = concordance_index_censored(y_test['event'], y_test['time'], predicted_risk)

    print(f"✅ Model trained with Concordance Index: {c_index[0]}")

    return pipeline

# implement model selection
# def train_model_2(
#         X_processed : pd.DataFrame,
#         y_train : pd.DataFrame
#     ) :

#     """
#     1. Get the pre-processed data from the pipeline
#     2. Implement the classification model
#     3. Return the model   """

#     # $CODE_BEGIN
#     print(Fore.BLUE + "\nTraining the model..." + Style.RESET_ALL)

#     # Classification model to predict positive probability
#     model = SVC(probability=True, class_weight='balanced')

#     grid = {
#             'C' : stats.uniform(0.1, 60),
#             'kernel': ['linear', 'rbf', 'sigmoid'],
#             'gamma' : stats.uniform(0.02, 0.06)
#             }
#     randsearch = RandomizedSearchCV(estimator=model, param_distributions=grid,
#                                     n_iter=3000, scoring='precision',
#                                     cv=3, n_jobs=-1, verbose=1)

#     # Perform cross-validation with precision scoring
#     randsearch.fit(X_processed, y_train)

#     print(f"✅ SVM Model trained with best params: {randsearch.best_params_} and best score: {randsearch.best_score_}")

#     return {
#         "model" : randsearch.best_estimator_,
#         "params" : randsearch.best_params_,
#         "score" : randsearch.best_score_
#         }
