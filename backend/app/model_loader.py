import os
import json
import pickle
import keras
from keras.models import load_model


# -------------------------------------------------
# Compatibility patch for older Keras models
# -------------------------------------------------

_original_dense_init = keras.layers.Dense.__init__

def patched_dense_init(self, *args, **kwargs):
    kwargs.pop("quantization_config", None)
    _original_dense_init(self, *args, **kwargs)

keras.layers.Dense.__init__ = patched_dense_init


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")


print("Loading models...")


# -------------------------
# LSTM
# -------------------------

LSTM_MODEL = load_model(
    os.path.join(
        MODEL_DIR,
        "lstm",
        "lstm_baseline_best.keras"
    ),
    compile=False
)


print("✓ LSTM loaded")


# -------------------------
# CNN LSTM
# -------------------------

CNN_MODEL = load_model(
    os.path.join(
        MODEL_DIR,
        "cnn_lstm",
        "cnn_lstm_hybrid_best.keras"
    ),
    compile=False
)


print("✓ CNN/LSTM loaded")


# -------------------------
# Scalers
# -------------------------

with open(
    os.path.join(MODEL_DIR, "scalers.pkl"),
    "rb"
) as f:

    SCALERS = pickle.load(f)


print("✓ Scalers loaded")


# -------------------------
# Feature Columns
# -------------------------

with open(
    os.path.join(
        MODEL_DIR,
        "feature_columns.json"
    ),
    "r"
) as f:

    FEATURE_COLUMNS = json.load(f)


print("✓ Feature columns loaded")