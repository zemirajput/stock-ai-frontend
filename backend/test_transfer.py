from app.transfer_prediction import predict_transfer_stock


try:
    result = predict_transfer_stock(
        ticker="AZN.L"
    )

    print(
        "\nChronos-2 Prediction result:"
    )

    for key, value in result.items():
        print(
            f"{key}: {value}"
        )

except Exception as error:
    print(
        "\nChronos-2 prediction failed:"
    )

    print(
        type(error).__name__,
        str(error)
    )