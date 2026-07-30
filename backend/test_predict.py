from app.predict import predict_stock


result = predict_stock(
    ticker="AZN.L",
    model_name="cnn_lstm"
)

print("\nCNN/LSTM Prediction result:")

for key, value in result.items():
    print(f"{key}: {value}")