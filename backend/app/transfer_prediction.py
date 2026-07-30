import os
import threading
from typing import Any

import numpy as np
import pandas as pd
import torch
import yfinance as yf

from chronos import Chronos2Pipeline


# -------------------------------------------------
# Paths
# -------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

CHRONOS_MODEL_DIR = os.path.join(
    MODEL_DIR,
    "chronos2"
)


# -------------------------------------------------
# Device settings
# -------------------------------------------------

if torch.cuda.is_available():
    DEVICE = "cuda"
    TORCH_DTYPE = torch.float32
else:
    DEVICE = "cpu"
    TORCH_DTYPE = torch.float32


# -------------------------------------------------
# Lazy-load Chronos-2 model
# -------------------------------------------------

CHRONOS_PIPELINE = None
CHRONOS_MODEL_LOCK = threading.Lock()


def get_chronos_pipeline() -> Chronos2Pipeline:
    """
    Load the Chronos-2 model only when it is first needed.

    Loading the model lazily allows FastAPI and Uvicorn to
    start and bind to the Render service port immediately.
    """

    global CHRONOS_PIPELINE

    if CHRONOS_PIPELINE is not None:
        return CHRONOS_PIPELINE

    with CHRONOS_MODEL_LOCK:
        # Check again in case another request loaded the model
        # while this request was waiting for the lock.
        if CHRONOS_PIPELINE is not None:
            return CHRONOS_PIPELINE

        print(
            "Loading Chronos-2 transfer-learning model...",
            flush=True
        )

        if not os.path.isdir(
            CHRONOS_MODEL_DIR
        ):
            raise FileNotFoundError(
                "Chronos-2 model folder was not found at: "
                f"{CHRONOS_MODEL_DIR}"
            )

        CHRONOS_PIPELINE = (
            Chronos2Pipeline.from_pretrained(
                CHRONOS_MODEL_DIR,
                device_map=DEVICE,
                dtype=TORCH_DTYPE
            )
        )

        print(
            f"Chronos-2 model loaded on {DEVICE}",
            flush=True
        )

    return CHRONOS_PIPELINE


# -------------------------------------------------
# Supported stock tickers
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


# -------------------------------------------------
# Download and prepare stock history
# -------------------------------------------------

def download_stock_history(
    ticker: str,
    period: str = "2y"
) -> pd.DataFrame:

    print(
        f"Downloading Chronos data for {ticker}...",
        flush=True
    )

    dataframe = yf.download(
        ticker,
        period=period,
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False
    )

    if dataframe is None or dataframe.empty:
        raise ValueError(
            f"No stock data was downloaded for {ticker}."
        )

    dataframe = dataframe.reset_index()

    # Fix yfinance MultiIndex columns
    if isinstance(
        dataframe.columns,
        pd.MultiIndex
    ):
        dataframe.columns = [
            column[0]
            if isinstance(column, tuple)
            else column
            for column in dataframe.columns
        ]

    if "Date" not in dataframe.columns:
        raise ValueError(
            "The downloaded data does not contain "
            "a Date column."
        )

    if "Close" not in dataframe.columns:
        raise ValueError(
            "The downloaded data does not contain "
            "a Close column."
        )

    dataframe = dataframe[
        [
            "Date",
            "Close"
        ]
    ].copy()

    dataframe["Date"] = pd.to_datetime(
        dataframe["Date"],
        errors="coerce"
    )

    # Remove timezone information if present
    if dataframe["Date"].dt.tz is not None:
        dataframe["Date"] = dataframe[
            "Date"
        ].dt.tz_localize(None)

    dataframe["Close"] = pd.to_numeric(
        dataframe["Close"],
        errors="coerce"
    )

    dataframe = dataframe.dropna(
        subset=[
            "Date",
            "Close"
        ]
    )

    dataframe = dataframe.sort_values(
        "Date"
    )

    dataframe = dataframe.drop_duplicates(
        subset=["Date"],
        keep="last"
    )

    # -------------------------------------------------
    # Convert irregular trading dates into a regular
    # business-day sequence
    # -------------------------------------------------

    dataframe = dataframe.set_index(
        "Date"
    )

    business_dates = pd.date_range(
        start=dataframe.index.min(),
        end=dataframe.index.max(),
        freq="B"
    )

    dataframe = dataframe.reindex(
        business_dates
    )

    # Fill holidays and missing business dates using
    # the previous closing price.
    dataframe["Close"] = dataframe[
        "Close"
    ].ffill()

    dataframe.index.name = "Date"

    dataframe = dataframe.reset_index()

    if dataframe["Close"].isna().any():
        dataframe["Close"] = dataframe[
            "Close"
        ].bfill()

    if len(dataframe) < 60:
        raise ValueError(
            f"Not enough historical data for {ticker}. "
            f"Only {len(dataframe)} rows were found."
        )

    inferred_frequency = pd.infer_freq(
        dataframe["Date"]
    )

    print(
        f"Chronos data frequency: "
        f"{inferred_frequency}",
        flush=True
    )

    print(
        f"Chronos history rows: "
        f"{len(dataframe)}",
        flush=True
    )

    return dataframe


# -------------------------------------------------
# Extract median forecast value
# -------------------------------------------------

def extract_prediction_value(
    forecast: Any
) -> float:

    # Chronos predict_df normally returns a DataFrame
    if isinstance(
        forecast,
        pd.DataFrame
    ):
        possible_columns = [
            "0.5",
            0.5,
            "median",
            "mean",
            "prediction"
        ]

        for column in possible_columns:
            if column in forecast.columns:
                return float(
                    forecast[
                        column
                    ].iloc[0]
                )

        numeric_columns = (
            forecast.select_dtypes(
                include=[np.number]
            ).columns
        )

        if len(numeric_columns) == 0:
            raise ValueError(
                "Chronos forecast contains no "
                "numeric prediction columns."
            )

        return float(
            forecast[
                numeric_columns[-1]
            ].iloc[0]
        )

    # Handle torch tensor output
    if torch.is_tensor(
        forecast
    ):
        values = (
            forecast
            .detach()
            .cpu()
            .numpy()
        )

        return float(
            np.median(
                values[..., 0]
            )
        )

    # Handle NumPy arrays and other array-like output
    values = np.asarray(
        forecast
    )

    if values.size == 0:
        raise ValueError(
            "Chronos returned an empty forecast."
        )

    return float(
        np.median(
            values[..., 0]
        )
    )


# -------------------------------------------------
# Transfer-learning prediction
# -------------------------------------------------

def predict_transfer_stock(
    ticker: str
) -> dict:

    ticker = ticker.upper().strip()

    if ticker not in SUPPORTED_TICKERS:
        raise ValueError(
            f"Ticker '{ticker}' is not supported. "
            f"Supported tickers: "
            f"{', '.join(SUPPORTED_TICKERS)}"
        )

    dataframe = download_stock_history(
        ticker=ticker
    )

    last_close = float(
        dataframe["Close"].iloc[-1]
    )

    # Rename columns into Chronos-2 format
    context_dataframe = dataframe.rename(
        columns={
            "Date": "timestamp",
            "Close": "target"
        }
    )

    context_dataframe[
        "item_id"
    ] = ticker

    context_dataframe = context_dataframe[
        [
            "item_id",
            "timestamp",
            "target"
        ]
    ].copy()

    # Load the model only when a Chronos prediction
    # is requested.
    pipeline = get_chronos_pipeline()

    # Make one-step-ahead forecast
    forecast = pipeline.predict_df(
        context_dataframe,
        prediction_length=1,
        quantile_levels=[
            0.1,
            0.5,
            0.9
        ],
        id_column="item_id",
        timestamp_column="timestamp",
        target="target"
    )

    predicted_price = (
        extract_prediction_value(
            forecast
        )
    )

    predicted_return = (
        predicted_price - last_close
    ) / last_close

    predicted_return_percent = (
        predicted_return * 100
    )

    # Chronos predicts price directly, so use the
    # predicted percentage movement for recommendation.
    if predicted_return_percent >= 0.5:
        direction = "UP"
        recommendation = "BUY"

    elif predicted_return_percent <= -0.5:
        direction = "DOWN"
        recommendation = "SELL"

    else:
        direction = "UNCERTAIN"
        recommendation = "HOLD"

    return {
        "ticker": ticker,
        "model": "transfer_learning",
        "last_close": round(
            last_close,
            4
        ),
        "predicted_return": round(
            predicted_return,
            6
        ),
        "predicted_return_percent": round(
            predicted_return_percent,
            4
        ),
        "predicted_price": round(
            predicted_price,
            4
        ),
        "direction": direction,
        "direction_probability": None,
        "recommendation": recommendation
    }