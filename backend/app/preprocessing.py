import json
import os
import pickle

import numpy as np
import pandas as pd
import yfinance as yf

from app.indicators import add_indicators


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

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)


# -------------------------------------------------
# Load feature-column configuration
# -------------------------------------------------

FEATURE_COLUMNS_PATH = os.path.join(
    MODEL_DIR,
    "feature_columns.json"
)

with open(
    FEATURE_COLUMNS_PATH,
    "r",
    encoding="utf-8"
) as file:
    FEATURE_COLUMNS = json.load(file)


PRICE_FEATURES = FEATURE_COLUMNS[
    "price_feature_cols"
]

MACRO_FEATURES = FEATURE_COLUMNS[
    "macro_feature_cols"
]

ALL_FEATURES = FEATURE_COLUMNS[
    "all_feature_cols"
]


# -------------------------------------------------
# Load saved scalers
# -------------------------------------------------

SCALERS_PATH = os.path.join(
    MODEL_DIR,
    "scalers.pkl"
)

with open(
    SCALERS_PATH,
    "rb"
) as file:
    SCALERS = pickle.load(file)

print("Scalers loaded", flush=True)


# -------------------------------------------------
# Date cleaning
# -------------------------------------------------

def clean_date_column(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Convert Date values into timezone-naive pandas
    datetime values.
    """

    if "Date" not in dataframe.columns:
        raise ValueError(
            "The dataframe does not contain a Date column."
        )

    dataframe = dataframe.copy()

    dataframe["Date"] = pd.to_datetime(
        dataframe["Date"],
        errors="coerce",
        utc=True
    )

    dataframe["Date"] = dataframe[
        "Date"
    ].dt.tz_localize(None)

    dataframe = dataframe.dropna(
        subset=["Date"]
    )

    return dataframe


# -------------------------------------------------
# Load fallback stock history
# -------------------------------------------------

def load_local_stock_data(
    ticker: str
) -> pd.DataFrame:
    """
    Load stock history from the local CSV when Yahoo
    Finance is unavailable or rate-limits Render.
    """

    fallback_path = os.path.join(
        DATA_DIR,
        "transfer_learning_series.csv"
    )

    if not os.path.isfile(
        fallback_path
    ):
        raise FileNotFoundError(
            "Yahoo Finance was unavailable and the "
            "fallback file was not found at: "
            f"{fallback_path}"
        )

    fallback = pd.read_csv(
        fallback_path
    )

    if "Ticker" not in fallback.columns:
        raise ValueError(
            "The fallback dataset does not contain "
            "a Ticker column."
        )

    fallback["Ticker"] = (
        fallback["Ticker"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    fallback = fallback[
        fallback["Ticker"] == ticker
    ].copy()

    if fallback.empty:
        raise ValueError(
            f"Yahoo Finance was unavailable and no "
            f"local data was found for {ticker}."
        )

    fallback = clean_date_column(
        fallback
    )

    required_stock_columns = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    missing_columns = [
        column
        for column in required_stock_columns
        if column not in fallback.columns
    ]

    if missing_columns:
        raise ValueError(
            "The fallback dataset cannot be used for "
            "stock prediction because it is missing: "
            + ", ".join(missing_columns)
        )

    for column in [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]:
        fallback[column] = pd.to_numeric(
            fallback[column],
            errors="coerce"
        )

    if "Adj Close" not in fallback.columns:
        fallback["Adj Close"] = fallback["Close"]

    fallback = fallback.replace(
        [np.inf, -np.inf],
        np.nan
    )

    fallback = fallback.dropna(
        subset=[
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]
    )

    fallback = fallback.sort_values(
        "Date"
    )

    fallback = fallback.drop_duplicates(
        subset=["Date"],
        keep="last"
    )

    print(
        f"Loaded {len(fallback)} local stock rows "
        f"for {ticker}.",
        flush=True
    )

    return fallback


# -------------------------------------------------
# Download stock data
# -------------------------------------------------

def get_stock_data(
    ticker: str
) -> pd.DataFrame:
    """
    Download historical stock prices from Yahoo.

    If Yahoo returns no data because of a rate limit,
    use the local training CSV as a fallback.
    """

    ticker = ticker.upper().strip()

    print(
        f"Downloading stock data for {ticker}...",
        flush=True
    )

    dataframe = pd.DataFrame()

    try:
        dataframe = yf.download(
            ticker,
            period="5y",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
            timeout=20,
            multi_level_index=False
        )

    except Exception as download_error:
        print(
            "Yahoo Finance download raised an error: "
            f"{download_error}",
            flush=True
        )

    if (
        dataframe is not None
        and not dataframe.empty
    ):
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

        dataframe = dataframe.reset_index()

        dataframe = clean_date_column(
            dataframe
        )

        dataframe = dataframe.sort_values(
            "Date"
        )

        dataframe = dataframe.drop_duplicates(
            subset=["Date"],
            keep="last"
        )

        print(
            f"Downloaded {len(dataframe)} Yahoo rows "
            f"for {ticker}.",
            flush=True
        )

        return dataframe

    print(
        "Yahoo Finance returned no stock data. "
        "Using local dataset fallback...",
        flush=True
    )

    return load_local_stock_data(
        ticker
    )


# -------------------------------------------------
# Add macro changes
# -------------------------------------------------

def add_macro_changes(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Add percentage-change columns for macroeconomic
    variables.
    """

    dataframe = dataframe.copy()

    macro_columns = [
        "inflation_rate",
        "interest_rate",
        "gdp_growth",
        "unemployment_rate",
        "exchange_rate",
        "FTSE100_Index"
    ]

    for column in macro_columns:
        change_column = f"{column}_Change"

        if (
            column in dataframe.columns
            and change_column not in dataframe.columns
        ):
            numeric_values = pd.to_numeric(
                dataframe[column],
                errors="coerce"
            )

            dataframe[change_column] = (
                numeric_values
                .pct_change(
                    fill_method=None
                )
                .replace(
                    [np.inf, -np.inf],
                    np.nan
                )
                .fillna(0.0)
            )

    return dataframe


# -------------------------------------------------
# Load macro data
# -------------------------------------------------

def load_macro_data(
    ticker: str
) -> pd.DataFrame:
    """
    Load macroeconomic features for the requested
    ticker.
    """

    macro_path = os.path.join(
        DATA_DIR,
        "transfer_learning_series.csv"
    )

    if not os.path.isfile(
        macro_path
    ):
        raise FileNotFoundError(
            "Macro dataset was not found at: "
            f"{macro_path}"
        )

    macro = pd.read_csv(
        macro_path
    )

    macro = clean_date_column(
        macro
    )

    if "Ticker" not in macro.columns:
        raise ValueError(
            "The macro dataset does not contain a "
            "Ticker column."
        )

    macro["Ticker"] = (
        macro["Ticker"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    macro = macro[
        macro["Ticker"] == ticker
    ].copy()

    if macro.empty:
        raise ValueError(
            f"No macro data was found for {ticker}."
        )

    macro = macro.sort_values(
        "Date"
    )

    macro = add_macro_changes(
        macro
    )

    macro = macro.drop_duplicates(
        subset=["Date"],
        keep="last"
    )

    print(
        f"Loaded {len(macro)} macro rows "
        f"for {ticker}.",
        flush=True
    )

    return macro


# -------------------------------------------------
# Validate model columns
# -------------------------------------------------

def validate_feature_columns(
    dataframe: pd.DataFrame
) -> None:
    """
    Confirm all model input columns exist.
    """

    missing_columns = [
        column
        for column in ALL_FEATURES
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Prepared data is missing these model "
            "features: "
            + ", ".join(missing_columns)
        )


# -------------------------------------------------
# Merge stock and macro data
# -------------------------------------------------

def merge_stock_and_macro(
    stock: pd.DataFrame,
    macro: pd.DataFrame
) -> pd.DataFrame:
    """
    Match every stock date with the latest available
    macroeconomic observation.
    """

    stock = stock.sort_values(
        "Date"
    ).copy()

    macro = macro.sort_values(
        "Date"
    ).copy()

    macro_columns_to_keep = [
        "Date"
    ]

    for column in MACRO_FEATURES:
        if (
            column in macro.columns
            and column not in macro_columns_to_keep
        ):
            macro_columns_to_keep.append(
                column
            )

    macro = macro[
        macro_columns_to_keep
    ].copy()

    dataframe = pd.merge_asof(
        stock,
        macro,
        on="Date",
        direction="backward"
    )

    available_macro_columns = [
        column
        for column in MACRO_FEATURES
        if column in dataframe.columns
    ]

    if available_macro_columns:
        dataframe[
            available_macro_columns
        ] = (
            dataframe[
                available_macro_columns
            ]
            .ffill()
            .bfill()
        )

    return dataframe


# -------------------------------------------------
# Prepare prediction input
# -------------------------------------------------

def prepare_input(
    ticker: str
):
    """
    Prepare a model input sequence with shape:

    (1, 60, number_of_features)
    """

    ticker = ticker.upper().strip()

    print(
        f"Preparing prediction input for {ticker}...",
        flush=True
    )

    # Stock prices
    stock = get_stock_data(
        ticker
    )

    print(
        f"Stock rows before indicators: {len(stock)}",
        flush=True
    )

    stock = add_indicators(
        stock
    )

    stock = clean_date_column(
        stock
    )

    stock = stock.sort_values(
        "Date"
    )

    print(
        f"Stock rows after indicators: {len(stock)}",
        flush=True
    )

    # Macro data
    macro = load_macro_data(
        ticker
    )

    # Merge stock and macro features
    dataframe = merge_stock_and_macro(
        stock=stock,
        macro=macro
    )

    dataframe = dataframe.sort_values(
        "Date"
    )

    dataframe = dataframe.replace(
        [np.inf, -np.inf],
        np.nan
    )

    validate_feature_columns(
        dataframe
    )

    # Convert model features to numeric values.
    for column in ALL_FEATURES:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce"
        )

    # Only remove rows missing actual model features.
    dataframe = dataframe.dropna(
        subset=ALL_FEATURES
    ).copy()

    print(
        "Complete processed rows available: "
        f"{len(dataframe)}",
        flush=True
    )

    if len(dataframe) < 60:
        raise ValueError(
            f"Not enough processed data for {ticker}. "
            f"Need 60 complete rows but found "
            f"{len(dataframe)}."
        )

    # Exact feature order used during training.
    features = dataframe[
        ALL_FEATURES
    ].copy()

    # Price scaler
    ticker_scalers = SCALERS.get(
        "ticker_scalers",
        {}
    )

    if ticker not in ticker_scalers:
        raise ValueError(
            f"No price scaler was found for {ticker}."
        )

    price_scaler = ticker_scalers[
        ticker
    ]

    features.loc[
        :,
        PRICE_FEATURES
    ] = price_scaler.transform(
        features[
            PRICE_FEATURES
        ]
    )

    # Macro scaler
    if "macro_scaler" not in SCALERS:
        raise ValueError(
            "The macro scaler was not found in "
            "scalers.pkl."
        )

    macro_scaler = SCALERS[
        "macro_scaler"
    ]

    features.loc[
        :,
        MACRO_FEATURES
    ] = macro_scaler.transform(
        features[
            MACRO_FEATURES
        ]
    )

    # Latest 60 days
    sequence = features.tail(
        60
    )

    if len(sequence) != 60:
        raise ValueError(
            f"Prediction sequence contains "
            f"{len(sequence)} rows instead of 60."
        )

    model_input = sequence.to_numpy(
        dtype=np.float32
    )

    model_input = np.expand_dims(
        model_input,
        axis=0
    )

    print(
        f"Model input shape: {model_input.shape}",
        flush=True
    )

    return model_input, dataframe