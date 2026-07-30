import os
import json
import pickle
import numpy as np
import pandas as pd
import yfinance as yf

from sklearn.preprocessing import MinMaxScaler

from app.indicators import add_indicators


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)


# -----------------------------
# Load feature columns
# -----------------------------

with open(
    os.path.join(
        MODEL_DIR,
        "feature_columns.json"
    ),
    "r"
) as f:
    FEATURE_COLUMNS = json.load(f)


PRICE_FEATURES = FEATURE_COLUMNS["price_feature_cols"]

MACRO_FEATURES = FEATURE_COLUMNS["macro_feature_cols"]

ALL_FEATURES = FEATURE_COLUMNS["all_feature_cols"]


# -----------------------------
# Load scalers
# -----------------------------

with open(
    os.path.join(
        MODEL_DIR,
        "scalers.pkl"
    ),
    "rb"
) as f:
    SCALERS = pickle.load(f)



# -----------------------------
# Load stock data
# -----------------------------

def get_stock_data(ticker):

    df = yf.download(
        ticker,
        period="2y",
        auto_adjust=False,
        progress=False
    )


    # Fix yfinance MultiIndex
    if isinstance(df.columns, pd.MultiIndex):

        df.columns = df.columns.get_level_values(0)


    df = df.reset_index()

    return df



# -----------------------------
# Add macro changes
# -----------------------------

def add_macro_changes(df):

    macro_cols = [
        "inflation_rate",
        "interest_rate",
        "gdp_growth",
        "unemployment_rate",
        "exchange_rate",
        "FTSE100_Index"
    ]


    for col in macro_cols:

        if col in df.columns:

            df[f"{col}_Change"] = (
                df[col]
                .pct_change()
                .fillna(0)
            )


    return df



# -----------------------------
# Load macro data
# -----------------------------

def load_macro_data():

    path = os.path.join(
        BASE_DIR,
        "data",
        "transfer_learning_series.csv"
    )


    macro = pd.read_csv(path)


    macro["Date"] = pd.to_datetime(
        macro["Date"]
    )


    macro = add_macro_changes(
        macro
    )


    return macro



# -----------------------------
# Prepare features
# -----------------------------

def prepare_input(ticker):


    print("Downloading stock data...")


    stock = get_stock_data(
        ticker
    )


    stock = add_indicators(
        stock
    )


    stock["Date"] = pd.to_datetime(
        stock["Date"]
    )


    print("Loading macro data...")


    macro = load_macro_data()


    macro = macro[
        macro["Ticker"] == ticker
    ]


    # Merge

        # Merge stock with macro data
    df = pd.merge(
        stock,
        macro,
        on="Date",
        how="left",
        suffixes=("", "_macro")
    )

    print("\n================ COLUMNS AFTER MERGE ================\n")
    for col in df.columns:
        print(col)
    print("\n=====================================================\n")

    df = df.sort_values(
        "Date"
    )


    df = df.dropna()


    print(
        "Features created:",
        len(df.columns)
    )



    # -----------------------------
    # Select exact 36 columns
    # -----------------------------

    features = df[
        ALL_FEATURES
    ].copy()


        # -----------------------------
    # Scale Features
    # -----------------------------

    ticker_scalers = SCALERS["ticker_scalers"]

    if ticker not in ticker_scalers:
        raise ValueError(f"No scaler found for ticker: {ticker}")

    price_scaler = ticker_scalers[ticker]

    features[PRICE_FEATURES] = price_scaler.transform(
        features[PRICE_FEATURES]
    )

    macro_scaler = SCALERS["macro_scaler"]

    features[MACRO_FEATURES] = macro_scaler.transform(
        features[MACRO_FEATURES]
    )

    # -----------------------------
    # Last 60 days
    # -----------------------------

    sequence = features.tail(60)


    if len(sequence) < 60:

        raise ValueError(
            "Not enough data. Need 60 days."
        )


    X = sequence.values


    X = np.expand_dims(
        X,
        axis=0
    )


    return X, df
