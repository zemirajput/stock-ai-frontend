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


# -------------------------------------------------
# Date cleaning helper
# -------------------------------------------------

def clean_date_column(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Convert the Date column to timezone-naive pandas
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
# Download stock data
# -------------------------------------------------

def get_stock_data(
    ticker: str
) -> pd.DataFrame:
    """
    Download enough history to create indicators and
    retain at least 60 complete input rows.
    """

    dataframe = yf.download(
        ticker,
        period="5y",
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False
    )

    if dataframe is None or dataframe.empty:
        raise ValueError(
            f"No stock data was downloaded for {ticker}."
        )

    # Fix yfinance MultiIndex columns.
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
        f"Downloaded {len(dataframe)} stock rows "
        f"for {ticker}.",
        flush=True
    )

    return dataframe


# -------------------------------------------------
# Add macro changes
# -------------------------------------------------

def add_macro_changes(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Add percentage-change columns for macro variables
    when those columns do not already exist.
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
            dataframe[change_column] = (
                pd.to_numeric(
                    dataframe[column],
                    errors="coerce"
                )
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
    Load and prepare macroeconomic data for one ticker.
    """

    macro_path = os.path.join(
        DATA_DIR,
        "transfer_learning_series.csv"
    )

    if not os.path.isfile(
        macro_path
    ):
        raise FileNotFoundError(
            "Macro data file was not found at: "
            f"{macro_path}"
        )

    macro = pd.read_csv(
        macro_path
    )

    macro = clean_date_column(
        macro
    )

    if "Ticker" in macro.columns:
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

    # Calculate percentage changes only after filtering
    # the data for the requested ticker.
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
# Validate required columns
# -------------------------------------------------

def validate_feature_columns(
    dataframe: pd.DataFrame
) -> None:
    """
    Confirm that every model feature exists before
    scaling and prediction.
    """

    missing_columns = [
        column
        for column in ALL_FEATURES
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "The prepared data is missing these model "
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
    Match each stock date with the most recent available
    macroeconomic observation.

    merge_asof is used because stock and macro dates do
    not necessarily occur on exactly the same day.
    """

    stock = stock.sort_values(
        "Date"
    ).copy()

    macro = macro.sort_values(
        "Date"
    ).copy()

    # Avoid duplicate stock-price columns from the macro
    # dataset. Keep Date and only columns needed by the
    # trained model.
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

    # Rows earlier than the first macro observation may
    # still be empty. Backfill them using the earliest
    # available macro values.
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
# Prepare model input
# -------------------------------------------------

def prepare_input(
    ticker: str
):
    """
    Prepare one model sequence with shape:

        (1, 60, number_of_features)
    """

    ticker = ticker.upper().strip()

    print(
        f"Preparing prediction input for {ticker}...",
        flush=True
    )

    # -------------------------------------------------
    # Stock data and technical indicators
    # -------------------------------------------------

    stock = get_stock_data(
        ticker
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

    # -------------------------------------------------
    # Macro data
    # -------------------------------------------------

    macro = load_macro_data(
        ticker
    )

    # -------------------------------------------------
    # Merge using the most recent macro observation
    # -------------------------------------------------

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

    # Convert model input columns to numeric.
    for column in ALL_FEATURES:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce"
        )

    # Drop rows only when one of the actual model
    # features is missing. Do not use dataframe.dropna()
    # on unrelated columns.
    dataframe = dataframe.dropna(
        subset=ALL_FEATURES
    ).copy()

    print(
        f"Complete processed rows available: "
        f"{len(dataframe)}",
        flush=True
    )

    if len(dataframe) < 60:
        raise ValueError(
            f"Not enough processed data for {ticker}. "
            f"Need 60 complete rows but found "
            f"{len(dataframe)}."
        )

    # -------------------------------------------------
    # Select features in the exact training order
    # -------------------------------------------------

    features = dataframe[
        ALL_FEATURES
    ].copy()

    # -------------------------------------------------
    # Scale price features
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Scale macro features
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Select the latest 60 complete rows
    # -------------------------------------------------

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