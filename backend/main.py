from pathlib import Path
from typing import Literal
import json

import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# -------------------------------------------------
# FastAPI application
# -------------------------------------------------

app = FastAPI(
    title="Stock AI Prediction API",
    description=(
        "Backend API for LSTM, CNN/LSTM, Chronos-2, "
        "historical stock prices and model analytics."
    ),
    version="1.2.0"
)


# -------------------------------------------------
# CORS settings
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# -------------------------------------------------
# Backend paths
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

ANALYTICS_DIR = BASE_DIR / "analytics"


# -------------------------------------------------
# Analytics files
# -------------------------------------------------

ANALYTICS_FILES = {
    "lstm": {
        "name": "LSTM",
        "metrics": (
            ANALYTICS_DIR
            / "lstm_baseline_metrics.json"
        ),
        "predictions": (
            ANALYTICS_DIR
            / "lstm_baseline_test_predictions.csv"
        )
    },

    "cnn_lstm": {
        "name": "CNN/LSTM",
        "metrics": (
            ANALYTICS_DIR
            / "cnn_lstm_hybrid_metrics.json"
        ),
        "predictions": (
            ANALYTICS_DIR
            / "cnn_lstm_hybrid_test_predictions.csv"
        )
    },

    "transfer_learning": {
        "name": "Chronos-2 Transfer Learning",
        "metrics": (
            ANALYTICS_DIR
            / "chronos2_transfer_learning_metrics.json"
        ),
        "predictions": (
            ANALYTICS_DIR
            / "chronos2_transfer_learning_test_predictions.csv"
        )
    }
}


# -------------------------------------------------
# Supported values
# -------------------------------------------------

SUPPORTED_TICKERS = [
    "AZN.L",
    "BLND.L",
    "BP.L",
    "CCC.L",
    "GSK.L",
    "LAND.L",
    "SGE.L",
    "SHEL.L",
    "TSCO.L",
    "ULVR.L"
]

SUPPORTED_MODELS = [
    "lstm",
    "cnn_lstm",
    "transfer_learning",
    "all"
]


# -------------------------------------------------
# Request model
# -------------------------------------------------

class PredictionRequest(BaseModel):
    ticker: str = Field(
        ...,
        examples=["AZN.L"]
    )

    model: Literal[
        "lstm",
        "cnn_lstm",
        "transfer_learning",
        "all"
    ] = Field(
        default="all",
        examples=["all"]
    )


# -------------------------------------------------
# Helper functions
# -------------------------------------------------

def validate_ticker(ticker: str) -> str:
    """
    Clean and validate a stock ticker.
    """

    cleaned_ticker = ticker.upper().strip()

    if cleaned_ticker not in SUPPORTED_TICKERS:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    f"Ticker '{cleaned_ticker}' "
                    "is not supported."
                ),
                "supported_tickers": SUPPORTED_TICKERS
            }
        )

    return cleaned_ticker


def get_column(
    dataframe: pd.DataFrame,
    column_name: str
) -> pd.Series:
    """
    Return a column from either a normal DataFrame
    or a yfinance MultiIndex DataFrame.
    """

    if column_name in dataframe.columns:
        column = dataframe[column_name]

        if isinstance(column, pd.DataFrame):
            return column.iloc[:, 0]

        return column

    if isinstance(
        dataframe.columns,
        pd.MultiIndex
    ):
        matching_columns = [
            column
            for column in dataframe.columns
            if column_name in column
        ]

        if matching_columns:
            column = dataframe[
                matching_columns[0]
            ]

            if isinstance(column, pd.DataFrame):
                return column.iloc[:, 0]

            return column

    raise ValueError(
        f"Column '{column_name}' was not found."
    )


def check_analytics_file(
    file_path: Path
) -> None:
    """
    Confirm that an analytics file exists.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Analytics file was not found: "
            f"{file_path.name}"
        )


def load_metrics(
    file_path: Path
) -> dict:
    """
    Read and format a model metrics JSON file.
    """

    check_analytics_file(file_path)

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        metrics = json.load(file)

    return {
        "rmse": round(
            float(metrics.get("RMSE", 0)),
            4
        ),
        "mae": round(
            float(metrics.get("MAE", 0)),
            4
        ),
        "mape": round(
            float(metrics.get("MAPE_%", 0)),
            4
        ),
        "r2": round(
            float(metrics.get("R2", 0)),
            6
        ),
        "direction_accuracy": round(
            float(
                metrics.get(
                    "Directional_Accuracy_%",
                    0
                )
            ),
            4
        )
    }


def load_prediction_samples(
    file_path: Path,
    ticker: str,
    sample_count: int
) -> list[dict]:
    """
    Read prediction samples for one ticker.
    """

    check_analytics_file(file_path)

    dataframe = pd.read_csv(file_path)

    required_columns = [
        "Date",
        "Ticker",
        "Actual_Close",
        "Predicted_Close"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Prediction file is missing columns: "
            + ", ".join(missing_columns)
        )

    dataframe["Ticker"] = (
        dataframe["Ticker"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    filtered_data = dataframe[
        dataframe["Ticker"] == ticker
    ].copy()

    if filtered_data.empty:
        return []

    filtered_data["Date"] = pd.to_datetime(
        filtered_data["Date"],
        errors="coerce"
    )

    filtered_data["Actual_Close"] = (
        pd.to_numeric(
            filtered_data["Actual_Close"],
            errors="coerce"
        )
    )

    filtered_data["Predicted_Close"] = (
        pd.to_numeric(
            filtered_data["Predicted_Close"],
            errors="coerce"
        )
    )

    filtered_data = (
        filtered_data
        .dropna(
            subset=[
                "Date",
                "Actual_Close",
                "Predicted_Close"
            ]
        )
        .sort_values("Date")
    )

    if len(filtered_data) > sample_count:
        sample_indexes = [
            round(index)
            for index in pd.Series(
                range(len(filtered_data))
            )
            .sample(
                n=sample_count,
                random_state=42
            )
            .sort_values()
            .tolist()
        ]

        filtered_data = filtered_data.iloc[
            sample_indexes
        ]

    samples = []

    for _, row in filtered_data.iterrows():
        samples.append({
            "date": row["Date"].strftime(
                "%Y-%m-%d"
            ),
            "display_date": row["Date"].strftime(
                "%d %b %Y"
            ),
            "ticker": ticker,
            "actual": round(
                float(row["Actual_Close"]),
                4
            ),
            "predicted": round(
                float(row["Predicted_Close"]),
                4
            )
        })

    return samples


def find_best_model(
    models: dict
) -> dict:
    """
    Find the best model using lowest RMSE.
    """

    available_models = [
        {
            "key": model_key,
            "name": model_data["name"],
            "rmse": model_data["metrics"]["rmse"],
            "mae": model_data["metrics"]["mae"],
            "mape": model_data["metrics"]["mape"],
            "r2": model_data["metrics"]["r2"],
            "direction_accuracy": (
                model_data["metrics"][
                    "direction_accuracy"
                ]
            )
        }
        for model_key, model_data
        in models.items()
    ]

    if not available_models:
        return {}

    best_model = min(
        available_models,
        key=lambda model: model["rmse"]
    )

    return best_model


# -------------------------------------------------
# Home route
# -------------------------------------------------

@app.get("/")
def home() -> dict:
    return {
        "message": (
            "Stock AI Prediction API is running."
        ),
        "status": "success",
        "models": [
            "LSTM",
            "CNN/LSTM",
            "Chronos-2 Transfer Learning"
        ],
        "endpoints": [
            "POST /predict",
            "GET /history/{ticker}",
            "GET /analytics",
            "GET /config",
            "GET /health"
        ]
    }


# -------------------------------------------------
# Health-check route
# -------------------------------------------------

@app.get("/health")
def health_check() -> dict:
    return {
        "status": "healthy",
        "api": "Stock AI Prediction API",
        "analytics_directory_exists": (
            ANALYTICS_DIR.exists()
        )
    }


# -------------------------------------------------
# Configuration route
# -------------------------------------------------

@app.get("/config")
def get_configuration() -> dict:
    return {
        "supported_tickers": SUPPORTED_TICKERS,
        "supported_models": SUPPORTED_MODELS
    }


# -------------------------------------------------
# Analytics route
# -------------------------------------------------

@app.get("/analytics")
def get_analytics(
    ticker: str = Query(
        default="AZN.L",
        description=(
            "Ticker used for actual-versus-predicted "
            "chart samples."
        )
    ),

    samples: int = Query(
        default=30,
        ge=5,
        le=100,
        description=(
            "Number of prediction samples returned "
            "for each model."
        )
    )
) -> dict:
    """
    Return real model metrics and test predictions.
    """

    cleaned_ticker = validate_ticker(ticker)

    try:
        models = {}

        for model_key, file_information in (
            ANALYTICS_FILES.items()
        ):
            metrics = load_metrics(
                file_information["metrics"]
            )

            prediction_samples = (
                load_prediction_samples(
                    file_path=(
                        file_information[
                            "predictions"
                        ]
                    ),
                    ticker=cleaned_ticker,
                    sample_count=samples
                )
            )

            models[model_key] = {
                "name": file_information["name"],
                "metrics": metrics,
                "predictions": prediction_samples
            }

        best_model = find_best_model(models)

        comparison = [
            {
                "key": model_key,
                "name": model_data["name"],
                "rmse": (
                    model_data["metrics"]["rmse"]
                ),
                "mae": (
                    model_data["metrics"]["mae"]
                ),
                "mape": (
                    model_data["metrics"]["mape"]
                ),
                "r2": (
                    model_data["metrics"]["r2"]
                ),
                "direction_accuracy": (
                    model_data["metrics"][
                        "direction_accuracy"
                    ]
                )
            }
            for model_key, model_data
            in models.items()
        ]

        return {
            "status": "success",
            "ticker": cleaned_ticker,
            "currency": "GBp",
            "unit": "pence",
            "sample_count": samples,
            "best_model": best_model,
            "comparison": comparison,
            "models": models,
            "training_history": {
                "available": False,
                "message": (
                    "Raw epoch-by-epoch training history "
                    "was not included in the exported "
                    "analytics files."
                ),
                "note": (
                    "Chronos-2 is a pretrained transfer-"
                    "learning model and does not use the "
                    "same local training-loss history as "
                    "LSTM and CNN/LSTM."
                )
            }
        }

    except FileNotFoundError as error:
        print(
            "Analytics file error:",
            str(error)
        )

        raise HTTPException(
            status_code=500,
            detail={
                "message": str(error),
                "expected_folder": str(
                    ANALYTICS_DIR
                ),
                "required_files": [
                    file_data["metrics"].name
                    for file_data
                    in ANALYTICS_FILES.values()
                ] + [
                    file_data["predictions"].name
                    for file_data
                    in ANALYTICS_FILES.values()
                ]
            }
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except Exception as error:
        print(
            "Analytics API error:",
            type(error).__name__,
            str(error)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Analytics request failed: "
                f"{type(error).__name__}: {error}"
            )
        ) from error


# -------------------------------------------------
# Historical-price route
# -------------------------------------------------

@app.get("/history/{ticker}")
def get_stock_history(
    ticker: str,

    days: int = Query(
        default=60,
        ge=5,
        le=365,
        description=(
            "Number of recent trading days to return."
        )
    )
) -> dict:

    cleaned_ticker = validate_ticker(ticker)

    try:
        # Download more calendar days than requested
        # because weekends and market holidays are excluded.
        download_period = (
            "2y"
            if days > 250
            else "1y"
        )

        history = yf.download(
            cleaned_ticker,
            period=download_period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if history is None or history.empty:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": (
                        "No historical data was found for "
                        f"'{cleaned_ticker}'."
                    )
                }
            )

        close_series = get_column(
            history,
            "Close"
        )

        history_data = (
            pd.DataFrame({
                "close": pd.to_numeric(
                    close_series,
                    errors="coerce"
                )
            })
            .dropna()
            .tail(days)
        )

        if history_data.empty:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": (
                        "Historical closing prices were "
                        "not available."
                    )
                }
            )

        prices = []

        for index, row in history_data.iterrows():
            date_value = pd.Timestamp(index)

            prices.append({
                "date": date_value.strftime(
                    "%d %b"
                ),
                "full_date": date_value.strftime(
                    "%Y-%m-%d"
                ),
                "close": round(
                    float(row["close"]),
                    4
                )
            })

        return {
            "status": "success",
            "ticker": cleaned_ticker,
            "currency": "GBp",
            "unit": "pence",
            "requested_days": days,
            "returned_days": len(prices),
            "history": prices
        }

    except HTTPException:
        raise

    except Exception as error:
        print(
            "Historical data API error:",
            type(error).__name__,
            str(error)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Historical-data request failed: "
                f"{type(error).__name__}: {error}"
            )
        ) from error


# -------------------------------------------------
# Prediction route
# -------------------------------------------------

@app.post("/predict")
def create_prediction(
    request: PredictionRequest
) -> dict:

    ticker = validate_ticker(
        request.ticker
    )

    model_name = (
        request.model
        .lower()
        .strip()
    )

    try:
        # -----------------------------------------
        # LSTM prediction
        # -----------------------------------------

        if model_name == "lstm":
            from app.predict import predict_stock

            prediction = predict_stock(
                ticker=ticker,
                model_name="lstm"
            )

            return {
                "status": "success",
                "ticker": ticker,
                "prediction": prediction
            }

        # -----------------------------------------
        # CNN/LSTM prediction
        # -----------------------------------------

        if model_name == "cnn_lstm":
            from app.predict import predict_stock

            prediction = predict_stock(
                ticker=ticker,
                model_name="cnn_lstm"
            )

            return {
                "status": "success",
                "ticker": ticker,
                "prediction": prediction
            }

        # -----------------------------------------
        # Chronos-2 prediction
        # -----------------------------------------

        if model_name == "transfer_learning":
            from app.transfer_prediction import predict_transfer_stock

            prediction = (
                predict_transfer_stock(
                    ticker=ticker
                )
            )

            return {
                "status": "success",
                "ticker": ticker,
                "prediction": prediction
            }

        # -----------------------------------------
        # Run all three models
        # -----------------------------------------

        if model_name == "all":
            raise HTTPException(
                status_code=400,
                detail={
                    "message": (
                        "The 'all' option is disabled on the Render "
                        "512 MiB free instance because loading TensorFlow "
                        "and Chronos together causes an out-of-memory "
                        "shutdown. Request one model at a time."
                    ),
                    "supported_single_models": [
                        "lstm",
                        "cnn_lstm",
                        "transfer_learning"
                    ]
                }
            )

        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    f"Model '{model_name}' "
                    "is not supported."
                ),
                "supported_models": SUPPORTED_MODELS
            }
        )

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except Exception as error:
        print(
            "Prediction API error:",
            type(error).__name__,
            str(error)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction failed: "
                f"{type(error).__name__}: {error}"
            )
        ) from error