import pandas as pd
from pydantic import BaseModel
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, File, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
import json
from employee_attrition.ml_logic.registry import load_model
# from employee_attrition.ml_logic.data import get_data, save_data_to_gcs, get_processed_data
from employee_attrition.interface.main import  predict_curves_on_data #train_model
from employee_attrition import params

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.state.model = load_model()


@app.get("/")
def root():
    return {
        "greeting": "works!"
    }
class RiskRequest(BaseModel):
    risk_scores_df: Dict[str, Any]  # Flexible dictionary structure
    num_samples: int = 10           # Default 10 samples

@app.post("/predictRisk")
def predict_risk(request: RiskRequest = Body(...)):
    try:
        # Convert input to DataFrame
        risk_scores_df = pd.DataFrame(request.risk_scores_df)

        # Validate
        if request.num_samples <= 0:
            raise HTTPException(status_code=400, detail="num_samples must be positive")
        if len(risk_scores_df) == 0:
            raise HTTPException(status_code=400, detail="Empty DataFrame received")

        top_n_high_risk, survival_df = predict_curves_on_data(app.state.model, risk_scores_df, request.num_samples)

        return {
            "top_n_high_risk": top_n_high_risk.to_dict("records"),
            "survival_df": survival_df.to_dict("records")
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")




# @app.get("/train_model")
# def train_model():
#     # 1. read the latest clean data from google cloud
#     # 2. preprocess it
#     # 3. train the model

#     success, message = train_model2(save=True)
#     if success:
#         model_dic = message
#         return {
#             "params" : model_dic['params'],
#             "score" : model_dic['score']
#         }

#     else :
#         return {
#             "Error" : f"Unable to train model, {message}"
#         }


# @app.post("/get_similar_users")
# def get_similar_users(File: UploadFile=File(...)):
#     content = File.file.read()
#     decode = content.decode('utf-8')
#     df_json = json.loads(decode)
#     X_pred = pd.DataFrame(df_json)

#     print("Received the prediction data")
#     print(X_pred)
#     X_processed = app.state.preproc_pipe.transform(X_pred)
#     print("Transformed the prediction data")
#     print(X_processed)
#     # Make prediction
#     # breakpoint()
#     try:
#         if params.DATA_TARGET == 'local':
#             print(" Reading the clean data from local folder: raw_data..")
#             data_for_ml = pd.read_csv(f"raw_data/{params.CLEANED_FILE_ML}", index_col=0)

#         elif params.DATA_TARGET == 'gcs':

#             print("Reading the clean data from gcs ..")
#             bucket_name = params.BUCKET_NAME
#             gsfile_path_events_ppl = f'gs://{bucket_name}/{params.CLEANED_FILE_ML}'
#             data_for_ml = pd.read_csv(gsfile_path_events_ppl)

#         # Processed the training data
#         X_train_processed = app.state.preproc_pipe.transform(data_for_ml)

#         # Find the indices of similar user based on cosine_similarity
#         user_id_indices = similar_users(X_train_processed, X_processed)

#         # Get the user information and send it back as a json
#         users_info = data_for_ml.iloc[user_id_indices][['jobTitle','company']]
#         users_info.index = users_info.index.astype(int)

#         # users_info.index.name = "User_ID"
#         # users_info.reset_index(inplace= True)

#         user_dict = users_info.to_json()
#         print(user_dict)

#         return user_dict

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
