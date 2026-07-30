import keras

# Patch Dense layer compatibility
original_dense_init = keras.layers.Dense.__init__

def patched_dense_init(self, *args, **kwargs):
    kwargs.pop("quantization_config", None)
    original_dense_init(self, *args, **kwargs)

keras.layers.Dense.__init__ = patched_dense_init


from keras.models import load_model


lstm_model = load_model(
    "models/lstm/lstm_baseline_best.keras",
    compile=False
)

cnn_model = load_model(
    "models/cnn_lstm/cnn_lstm_hybrid_best.keras",
    compile=False
)


print("LSTM Input Shape:")
print(lstm_model.input_shape)

print("\nLSTM Output Shape:")
print(lstm_model.output_shape)


print("\nCNN/LSTM Input Shape:")
print(cnn_model.input_shape)

print("\nCNN/LSTM Output Shape:")
print(cnn_model.output_shape)