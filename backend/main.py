
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://work-linear-reguration-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# DATASET CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "study_hours_exam_scores.csv"

PASS_MARK = 50


def load_dataset():
    """Load and validate the study hours dataset."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_PATH}"
        )

    dataset = pd.read_csv(DATA_PATH)

    required_columns = ["Study_Hours", "Exam_Score"]

    for column in required_columns:
        if column not in dataset.columns:
            raise ValueError(
                f"CSV must contain the column: {column}"
            )

    if dataset.empty:
        raise ValueError("The CSV dataset is empty.")

    # Ensure required values are numeric.
    for column in required_columns:
        dataset[column] = pd.to_numeric(
            dataset[column], errors="coerce"
        )

    dataset = dataset.dropna(subset=required_columns)

    if dataset.empty:
        raise ValueError(
            "The dataset contains no valid numeric rows."
        )

    return dataset


# ==================================================
# LOAD DATASET
# ==================================================

try:
    df = load_dataset()
    print(f"Dataset loaded successfully: {len(df)} rows")

except Exception as error:
    print(f"Dataset error: {error}")
    df = pd.DataFrame()


# ==================================================
# REQUEST MODEL
# ==================================================

class AnalysisRequest(BaseModel):
    study_hours: float = Field(
        ...,
        ge=0,
        description="Number of hours studied by the student",
    )


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def get_relationship(r_value: float) -> str:
    """Describe the direction and strength of correlation."""

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
        "message": "Correlation vs Linear Regression API is running.",
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
def analyze(request: AnalysisRequest):
    if df.empty:
        raise HTTPException(
            status_code=500,
            detail="Dataset could not be loaded.",
        )

    study_hours = request.study_hours

    # Correlation is calculated from the dataset.
    x_values = df["Study_Hours"]
    y_values = df["Exam_Score"]

    if len(df) < 2 or x_values.nunique() < 2 or y_values.nunique() < 2:
        raise HTTPException(
            status_code=422,
            detail=(
                "At least two valid rows with variation "
                "in study hours and exam scores are required."
            ),
        )

    correlation, p_value = pearsonr(x_values, y_values)
    relationship = get_relationship(float(correlation))

    # Fit linear regression to the dataset.
    X = df[["Study_Hours"]]
    y = df["Exam_Score"]

    model = LinearRegression()
    model.fit(X, y)

    predicted_score = float(
        model.predict(pd.DataFrame({"Study_Hours": [study_hours]}))[0]
    )

    slope = float(model.coef_[0])
    intercept = float(model.intercept_)

    # PASS / FAIL classification.
    result = "PASS" if predicted_score >= PASS_MARK else "FAIL"

    return {
        "study_hours": round(study_hours, 2),
        "regression": {
            "predicted_score": round(predicted_score, 2),
            "pass_mark": PASS_MARK,
            "result": result,
            "equation": (
                f"Exam Score = {slope:.2f} × Study Hours "
                f"+ {intercept:.2f}"
            ),
        },
        "correlation": {
            "pearson_r": round(float(correlation), 4),
            "p_value": round(float(p_value), 4),
            "relationship": relationship,
            "explanation": (
                "Correlation measures the strength and direction "
                "of the linear relationship between study hours "
                "and exam scores in the dataset. It does not predict "
                "an individual student's exam score or PASS/FAIL result."
            ),
        },
    }
