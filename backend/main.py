from fastapi import FastAPI
import uvicorn
<<<<<<< HEAD
import joblib
import pandas as pd
=======
>>>>>>> 6da8e07e73dcf8da0a590226f0184853142cc9bc

app = FastAPI()

print("✅ Server starting on http://localhost:8000")

<<<<<<< HEAD
# -------------------------------
# Load Trained Model Once
# -------------------------------
model = joblib.load("models/xgboost_fraud_model.pkl")


# -------------------------------
# Home Route
# -------------------------------
=======
>>>>>>> 6da8e07e73dcf8da0a590226f0184853142cc9bc
@app.get("/")
def home():
    return {"message": "Insurance Claims API"}

<<<<<<< HEAD

# -------------------------------
# Dashboard Stats Route
# -------------------------------
=======
>>>>>>> 6da8e07e73dcf8da0a590226f0184853142cc9bc
@app.get("/dashboard/stats")
def stats():
    return {
        "total_claims": 250,
        "today_claims": 8,
        "pending_review": 15,
<<<<<<< HEAD
        "fraud_probability": 0.38  # You can later connect this dynamically
    }


# -------------------------------
# Prediction Route
# -------------------------------
@app.post("/predict")
def predict(claim: dict):
    """
    Expected JSON:
    {
        "patient_age": 60,
        "claimed_amount": 250000
    }
    """

    df = pd.DataFrame([claim])

    prob = model.predict_proba(df)[0][1]
    prediction = int(model.predict(df)[0])

    return {
        "fraud_probability": float(prob),
        "prediction": prediction
    }


# -------------------------------
# Run Server
# -------------------------------
=======
        "fraud_probability": 0.38
    }

# This keeps the server running
>>>>>>> 6da8e07e73dcf8da0a590226f0184853142cc9bc
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)