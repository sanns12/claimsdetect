from fastapi import FastAPI
import uvicorn

app = FastAPI()

print("✅ Server starting on http://localhost:8000")

@app.get("/")
def home():
    return {"message": "Insurance Claims API"}

@app.get("/dashboard/stats")
def stats():
    return {
        "total_claims": 250,
        "today_claims": 8,
        "pending_review": 15,
        "fraud_probability": 0.38
    }

# This keeps the server running
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)