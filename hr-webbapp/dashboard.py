import streamlit as st
import requests
import pandas as pd
import mlflow.pyfunc

# Load model from MLflow
MLFLOW_TRACKING_URI = "http://your-mlflow-server.com"  # Update with your MLflow server
MODEL_NAME = "employee_attrition"
MODEL_STAGE = "Production"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_STAGE}")

# Streamlit UI
st.title("Employee Attrition Risk Dashboard")

# Fetch employee data
api_url = "http://localhost:8000/employees"
response = requests.get(api_url)
if response.status_code == 200:
    employees = pd.DataFrame(response.json())
else:
    st.error("Failed to fetch employee data")
    employees = pd.DataFrame()

# Predict attrition risk
if not employees.empty:
    employees["attrition_risk"] = model.predict(employees.drop(columns=["EmployeeID"]))
    high_risk = employees.sort_values(by="attrition_risk", ascending=False)

    # Display top at-risk employees
    num_top = st.slider("Select number of high-risk employees to view", 1, 20, 5)
    st.write(high_risk.head(num_top))

    # Placeholder for survival curves & risk factor insights
    st.subheader("Survival Curves for High-Risk Employees")
    st.write("(Visualization placeholder)")

    st.subheader("Risk Factors & HR Recommendations")
    st.write("(Analysis placeholder)")

else:
    st.warning("No employee data available.")
