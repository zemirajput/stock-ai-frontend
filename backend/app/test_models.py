import keras
from keras.models import load_model
import pickle


# Patch Dense layer to ignore quantization_config
original_dense_init = keras.layers.Dense.__init__

def patched_dense_init(self, *args, **kwargs):
    kwargs.pop("quantization_config", None)
    original_dense_init(self, *args, **kwargs)

keras.layers.Dense.__init__ = patched_dense_init


print("Testing LSTM model...")

lstm_model = load_model(
    "models/lstm/lstm_baseline_best.keras",
    compile=False
)

print("✅ LSTM model loaded successfully")


print("Testing CNN/LSTM model...")

cnn_model = load_model(
    "models/cnn_lstm/cnn_lstm_hybrid_best.keras",
    compile=False
)

print("✅ CNN/LSTM model loaded successfully")


print("Testing scaler...")

with open("models/scalers.pkl", "rb") as file:
    scaler = pickle.load(file)

print("✅ Scaler loaded successfully")


print("\n🎉 All files are working correctly!")