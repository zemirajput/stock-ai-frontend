import os
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
# Load Chronos-2 model
# -------------------------------------------------

print(
    "Loading Chronos-2 transfer-learning model..."
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
    f"✓ Chronos-2 model loaded on {DEVICE}"
)


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
        f"Downloading Chronos data for {ticker}..."
    )

    dataframe = yf.download(
        ticker,
        period=period,
        interval="1d",
        auto_adjust=False,
        progress=False
    )

    if dataframe.empty:
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
    # the previous closing price
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
        f"{inferred_frequency}"
    )

    print(
        f"Chronos history rows: "
        f"{len(dataframe)}"
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

    # Make one-step-ahead forecast
    forecast = CHRONOS_PIPELINE.predict_df(
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
    # predicted percentage movement for recommendation
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