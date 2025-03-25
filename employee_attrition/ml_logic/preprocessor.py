
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin

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


def preprocess_features(X: pd.DataFrame, save_pipeline = True):

    # Preprocess features
    # Feature Selection from the merged dataset

    preprocessor_pipe = ColumnTransformer(
            [
                ("employment_pipe", employment_pipe, ["jobDateRange"]),
                ("job_duration_pipe", job_duration_pipe, ["jobDuration", "jobDuration2"] ),
                ("schoolPassed_pipe", schoolPassed_pipe, ["schoolDateRange"]),
                ('metadata_pipe', metadata_pipe, metadata_columns)
            ],
            remainder='drop'
        )

    final_preprocessor = Pipeline([
                                ('preprocessor', preprocessor_pipe),
                                ('scaler', MinMaxScaler())
                                ])

    X_processed = final_preprocessor.fit_transform(X)
    # print(X_processed[:5, :5])

    print("✅ X_processed, with shape", X_processed.shape)

    print(X_processed)

    if save_pipeline == True:
        save_preproc_pipeline(final_preprocessor)

    return X_processed
