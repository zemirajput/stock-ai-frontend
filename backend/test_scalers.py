import pickle

with open("models/scalers.pkl", "rb") as f:
    scalers = pickle.load(f)

print(type(scalers))

print("\nTop level keys:")
print(scalers.keys())

print("\nTicker scaler keys:")

ticker_scalers = scalers["ticker_scalers"]

print(type(ticker_scalers))

print(list(ticker_scalers.keys()))