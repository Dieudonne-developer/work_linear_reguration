```python
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression


# ==================================================
# APP CONFIGURATION
# ==================================================

app = FastAPI(
    title="Correlation vs Linear Regression API",
    description=(
        "A simple API demonstrating the difference "
        "between correlation and linear regression."
    ),
    version="1.0.0",
)


# ==================================================
# CORS CONFIGURATION
# ==================================================
# These origins allow both local development and
# the deployed React frontend to communicate with
# this FastAPI backend.
#
# IMPORTANT:
# Replace the frontend Render URL below with your
# actual frontend URL if it is different.
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        # Deployed frontend
        "https://work-linear-reguration.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# DATASET CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "study_hours_exam_scores.csv"
)

PASS_MARK = 50


def load_dataset():
    """
    Load and validate the study hours dataset.
    """

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "Study_Hours",
        "Exam_Score",
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"CSV must contain the column: {column}"
            )

    if df.empty:
        raise ValueError(
            "The CSV dataset is empty."
        )

    return df


# ==================================================
# LOAD DATASET
# ==================================================

try:
    df = load_dataset()

    print(
        f"Dataset loaded successfully: "
        f"{len(df)} rows"
    )

except Exception as error:
    print(
        f"Dataset error: {error}"
    )

    df = pd.DataFrame()


# ==================================================
# REQUEST MODEL
# ==================================================

class AnalysisRequest(BaseModel):
    study_hours: float = Field(
        ...,
        ge=0,
        description=(
            "Number of hours studied by the student"
        ),
    )


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def get_relationship(
    r_value: float,
) -> str:
    """
    Convert Pearson correlation value into
    a human-readable relationship description.
    """

    if r_value >= 0.7:
        return "Strong positive relationship"

    elif r_value >= 0.3:
        return "Moderate positive relationship"

    elif r_value > -0.3:
        return "Weak or no linear relationship"

    elif r_value > -0.7:
        return "Moderate negative relationship"

    else:
        return "Strong negative relationship"


# ==================================================
# ROOT ROUTE
# ==================================================

@app.get("/")
def root():
    return {
        "message": (
            "Correlation vs Linear Regression "
            "API is running."
        ),
        "status": "success",
        "docs": "/docs",
    }


# ==================================================
# API INFORMATION
# ==================================================

@app.get("/api/info")
def get_info():

    if df.empty:
        raise HTTPException(
            status_code=500,
            detail="Dataset could not be loaded.",
        )

    return {
        "dataset": "study_hours_exam_scores.csv",
        "rows": len(df),
        "pass_mark": PASS_MARK,
    }


# ==================================================
# ANALYSIS ROUTE
# ==================================================

@app.post("/api/analyze")
def analyze(
    request: AnalysisRequest,
):

    # ------------------------------------------------
    # Check dataset
    # ------------------------------------------------

    if df.empty:
        raise HTTPException(
            status_code=500,
            detail="Dataset could not be loaded.",
        )

    study_hours = request.study_hours

    # ==================================================
    # CORRELATION
    # ==================================================

    correlation, p_value = pearsonr(
        df["Study_Hours"],
        df["Exam_Score"],
    )

    relationship = get_relationship(
        float(correlation)
    )

    # ==================================================
    # LINEAR REGRESSION
    # ==================================================

    X = df[["Study_Hours"]]

    y = df["Exam_Score"]

    model = LinearRegression()

    model.fit(X, y)

    predicted_score = model.predict(
        [[study_hours]]
    )[0]

    slope = model.coef_[0]

    intercept = model.intercept_

    # ==================================================
    # PASS / FAIL
    # ==================================================

    result = (
        "PASS"
        if predicted_score >= PASS_MARK
        else "FAIL"
    )

    # ==================================================
    # RESPONSE
    # ==================================================

    return {
        "study_hours": round(
            study_hours,
            2,
        ),

        "regression": {
            "predicted_score": round(
                float(predicted_score),
                2,
            ),

            "pass_mark": PASS_MARK,

            "result": result,

            "equation": (
                "Exam Score = "
                f"{slope:.2f} × Study Hours + "
                f"{intercept:.2f}"
            ),
        },

        "correlation": {
            "pearson_r": round(
                float(correlation),
                2,
            ),

            "p_value": round(
                float(p_value),
                4,
            ),

            "relationship": relationship,

            "explanation": (
                "Correlation measures the strength "
                "and direction of the relationship "
                "between study hours and exam scores "
                "in the dataset. It does not predict "
                "an individual student's exam score "
                "or PASS/FAIL result."
            ),
        },
    }
```
