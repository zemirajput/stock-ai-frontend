import gc
import os
import pickle
from typing import Any

import numpy as np


# -------------------------------------------------
# Paths
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
SCALERS_PATH = os.path.join(MODEL_DIR, "scalers.pkl")


# -------------------------------------------------
# Supported tickers
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
# Lazy-loaded scaler cache
# -------------------------------------------------

SCALERS: dict[str, Any] | None = None


def get_scalers() -> dict[str, Any]:
    """Load the scaler file only when a prediction is requested."""

    global SCALERS

    if SCALERS is None:
        if not os.path.isfile(SCALERS_PATH):
            raise FileNotFoundError(
                f"Scaler file was not found at: {SCALERS_PATH}"
            )

        with open(SCALERS_PATH, "rb") as file:
            SCALERS = pickle.load(file)

        print("Scalers loaded", flush=True)

    return SCALERS


# -------------------------------------------------
# Keras compatibility and model loading
# -------------------------------------------------

def load_prediction_model(model_name: str):
    """
    Import Keras and load only the model selected by the request.

    The model is not kept globally, which helps reduce memory pressure on
    Render's 512 MiB free instance after each prediction finishes.
    """

    import keras
    from keras.models import load_model

    original_dense_init = keras.layers.Dense.__init__

    if not getattr(keras.layers.Dense.__init__, "_stock_ai_patched", False):
        def patched_dense_init(self, *args, **kwargs):
            kwargs.pop("quantization_config", None)
            original_dense_init(self, *args, **kwargs)

        patched_dense_init._stock_ai_patched = True
        keras.layers.Dense.__init__ = patched_dense_init

    if model_name == "lstm":
        model_path = os.path.join(
            MODEL_DIR,
            "lstm",
            "lstm_baseline_best.keras"
        )

    elif model_name in {"cnn", "cnn_lstm", "cnn-lstm"}:
        model_path = os.path.join(
            MODEL_DIR,
            "cnn_lstm",
            "cnn_lstm_hybrid_best.keras"
        )

    else:
        raise ValueError(
            "Invalid model name. Use 'lstm' or 'cnn_lstm'."
        )

    if not os.path.isfile(model_path):
        raise FileNotFoundError(
            f"Prediction model was not found at: {model_path}"
        )

    print(f"Loading {model_name} model...", flush=True)

    return load_model(
        model_path,
        compile=False
    )


# -------------------------------------------------
# Prediction function
# -------------------------------------------------

def predict_stock(ticker: str, model_name: str = "lstm") -> dict:
    ticker = ticker.upper().strip()
    model_name = model_name.lower().strip()

    if ticker not in SUPPORTED_TICKERS:
        raise ValueError(
            f"Ticker '{ticker}' is not supported. "
            f"Supported tickers: {', '.join(SUPPORTED_TICKERS)}"
        )

    if model_name not in {"lstm", "cnn", "cnn_lstm", "cnn-lstm"}:
        raise ValueError(
            "Invalid model name. Use 'lstm' or 'cnn_lstm'."
        )

    model = None

    try:
        # These heavy imports now happen only after the API is already live.
        from app.preprocessing import prepare_input

        scalers = get_scalers()
        model = load_prediction_model(model_name)

        # Create input with shape (1, 60, 36)
        X, dataframe = prepare_input(ticker)

        predictions = model.predict(
            X,
            verbose=0
        )

        predicted_return_scaled = float(
            np.asarray(predictions[0]).reshape(-1)[0]
        )

        direction_probability = float(
            np.asarray(predictions[1]).reshape(-1)[0]
        )

        ticker_scaler = scalers["ticker_scalers"][ticker]
        daily_return_index = PRICE_FEATURES.index("Daily_Return")

        inverse_input = np.zeros(
            (1, len(PRICE_FEATURES))
        )

        inverse_input[0, daily_return_index] = (
            predicted_return_scaled
        )

        inverse_result = ticker_scaler.inverse_transform(
            inverse_input
        )

        predicted_return = float(
            inverse_result[0, daily_return_index]
        )

        last_close = float(
            dataframe["Close"].iloc[-1]
        )

        predicted_price = last_close * (1 + predicted_return)

        if direction_probability >= 0.55:
            predicted_direction = "UP"
            recommendation = "BUY"
        elif direction_probability <= 0.45:
            predicted_direction = "DOWN"
            recommendation = "SELL"
        else:
            predicted_direction = "UNCERTAIN"
            recommendation = "HOLD"

        normalized_model_name = (
            "cnn_lstm"
            if model_name in {"cnn", "cnn_lstm", "cnn-lstm"}
            else "lstm"
        )

        return {
            "ticker": ticker,
            "model": normalized_model_name,
            "last_close": round(last_close, 4),
            "predicted_return": round(predicted_return, 6),
            "predicted_return_percent": round(
                predicted_return * 100,
                4
            ),
            "predicted_price": round(predicted_price, 4),
            "direction": predicted_direction,
            "direction_probability": round(
                direction_probability,
                4
            ),
            "recommendation": recommendation
        }

    finally:
        # Release the loaded model after the request. TensorFlow itself may
        # retain some memory, but this prevents both models being held at once.
        if model is not None:
            del model

        try:
            import keras
            keras.backend.clear_session()
        except Exception:
            pass

        gc.collect()