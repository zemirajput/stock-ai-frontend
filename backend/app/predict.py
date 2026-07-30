import os
import pickle
import numpy as np
import keras

from keras.models import load_model
from app.preprocessing import prepare_input


# -------------------------------------------------
# Compatibility patch for saved Keras models
# -------------------------------------------------

_original_dense_init = keras.layers.Dense.__init__


def patched_dense_init(self, *args, **kwargs):
    kwargs.pop("quantization_config", None)
    _original_dense_init(self, *args, **kwargs)


keras.layers.Dense.__init__ = patched_dense_init


# -------------------------------------------------
# Paths
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")


# -------------------------------------------------
# Load models and scalers
# -------------------------------------------------

print("Loading prediction models...")

LSTM_MODEL = load_model(
    os.path.join(
        MODEL_DIR,
        "lstm",
        "lstm_baseline_best.keras"
    ),
    compile=False
)

print("✓ LSTM model loaded")

CNN_MODEL = load_model(
    os.path.join(
        MODEL_DIR,
        "cnn_lstm",
        "cnn_lstm_hybrid_best.keras"
    ),
    compile=False
)

print("✓ CNN/LSTM model loaded")

with open(
    os.path.join(
        MODEL_DIR,
        "scalers.pkl"
    ),
    "rb"
) as file:
    SCALERS = pickle.load(file)

print("✓ Scalers loaded")


# -------------------------------------------------
# Supported tickers
# -------------------------------------------------

SUPPORTED_TICKERS = list(
    SCALERS["ticker_scalers"].keys()
)


# -------------------------------------------------
# Price feature columns
# -------------------------------------------------

PRICE_FEATURES = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "SMA_10",
    "SMA_50",
    "EMA_10",
    "EMA_50",
    "RSI_14",
    "MACD",
    "MACD_Signal",
    "MACD_Hist",
    "Bollinger_Mid",
    "Bollinger_Upper",
    "Bollinger_Lower",
    "ATR_14",
    "OBV",
    "Daily_Return",
    "Volatility_10",
    "Momentum_10",
    "Return_Lag_1",
    "Return_Lag_2",
    "Return_Lag_3"
]


# -------------------------------------------------
# Prediction function
# -------------------------------------------------

def predict_stock(ticker: str, model_name: str = "lstm"):
    ticker = ticker.upper()
    model_name = model_name.lower()

    # Check ticker
    if ticker not in SUPPORTED_TICKERS:
        raise ValueError(
            f"Ticker '{ticker}' is not supported. "
            f"Supported tickers: {', '.join(SUPPORTED_TICKERS)}"
        )

    # Select model
    if model_name == "lstm":
        model = LSTM_MODEL

    elif model_name in [
        "cnn",
        "cnn_lstm",
        "cnn-lstm"
    ]:
        model = CNN_MODEL

    else:
        raise ValueError(
            "Invalid model name. "
            "Use 'lstm' or 'cnn_lstm'."
        )

    # Create input with shape (1, 60, 36)
    X, dataframe = prepare_input(ticker)

    # Make model prediction
    predictions = model.predict(
        X,
        verbose=0
    )

    # First output: scaled next-day return
    predicted_return_scaled = float(
        np.asarray(
            predictions[0]
        ).reshape(-1)[0]
    )

    # Second output: probability of upward movement
    direction_probability = float(
        np.asarray(
            predictions[1]
        ).reshape(-1)[0]
    )

    # Get ticker-specific scaler
    ticker_scaler = SCALERS[
        "ticker_scalers"
    ][ticker]

    # Locate Daily_Return in the feature list
    daily_return_index = PRICE_FEATURES.index(
        "Daily_Return"
    )

    # Create an empty scaled feature row
    inverse_input = np.zeros(
        (1, len(PRICE_FEATURES))
    )

    # Insert predicted scaled return
    inverse_input[
        0,
        daily_return_index
    ] = predicted_return_scaled

    # Convert scaled return to original value
    inverse_result = ticker_scaler.inverse_transform(
        inverse_input
    )

    predicted_return = float(
        inverse_result[
            0,
            daily_return_index
        ]
    )

    # Get latest actual closing price
    last_close = float(
        dataframe["Close"].iloc[-1]
    )

    # Calculate predicted next price
    predicted_price = (
        last_close
        * (1 + predicted_return)
    )

    # -------------------------------------------------
    # Direction and recommendation
    # -------------------------------------------------

    if direction_probability >= 0.55:
        predicted_direction = "UP"

    elif direction_probability <= 0.45:
        predicted_direction = "DOWN"

    else:
        predicted_direction = "UNCERTAIN"

    if direction_probability >= 0.55:
        recommendation = "BUY"

    elif direction_probability <= 0.45:
        recommendation = "SELL"

    else:
        recommendation = "HOLD"

    # -------------------------------------------------
    # Return result
    # -------------------------------------------------

    return {
        "ticker": ticker,
        "model": model_name,
        "last_close": round(
            last_close,
            4
        ),
        "predicted_return": round(
            predicted_return,
            6
        ),
        "predicted_return_percent": round(
            predicted_return * 100,
            4
        ),
        "predicted_price": round(
            predicted_price,
            4
        ),
        "direction": predicted_direction,
        "direction_probability": round(
            direction_probability,
            4
        ),
        "recommendation": recommendation
    }