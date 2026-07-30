function MultiModelResult({ result }) {
  if (
    !result ||
    !result.predictions
  ) {
    return null;
  }


  const formatPrice = (price) => {
    const numericPrice = Number(price);

    if (!Number.isFinite(numericPrice)) {
      return "N/A";
    }

    /*
      Yahoo Finance returns London Stock Exchange
      prices in pence.

      Example:
      12940 pence = £129.40
    */
    const priceInPounds = numericPrice / 100;

    return new Intl.NumberFormat(
      "en-GB",
      {
        style: "currency",
        currency: "GBP",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }
    ).format(priceInPounds);
  };


  const formatProbability = (probability) => {
    const numericProbability = Number(
      probability
    );

    if (!Number.isFinite(numericProbability)) {
      return "Not available";
    }

    return `${(
      numericProbability * 100
    ).toFixed(2)}%`;
  };


  const modelResults = [
    {
      key: "lstm",
      name: "LSTM",
      data: result.predictions.lstm
    },
    {
      key: "cnn_lstm",
      name: "CNN/LSTM",
      data: result.predictions.cnn_lstm
    },
    {
      key: "transfer_learning",
      name: "Transfer Learning",
      data: result.predictions.transfer_learning
    }
  ];


  const getRecommendationColour = (
    recommendation
  ) => {
    if (recommendation === "BUY") {
      return "text-green-400";
    }

    if (recommendation === "SELL") {
      return "text-red-400";
    }

    return "text-yellow-400";
  };


  const getDirectionColour = (
    direction
  ) => {
    if (direction === "UP") {
      return "text-green-400";
    }

    if (direction === "DOWN") {
      return "text-red-400";
    }

    return "text-yellow-400";
  };


  return (
    <div className="mt-8">
      <h2
        className="
          text-2xl
          font-bold
          text-white
          mb-6
        "
      >
        Prediction Comparison
      </h2>


      <div
        className="
          grid
          grid-cols-1
          md:grid-cols-2
          xl:grid-cols-3
          gap-6
        "
      >
        {modelResults.map((model) => {
          const prediction = model.data;

          if (!prediction) {
            return null;
          }

          return (
            <div
              key={model.key}
              className="
                bg-slate-900
                rounded-xl
                p-6
                text-white
                shadow-lg
                border
                border-slate-700
              "
            >
              <h3 className="text-xl font-bold">
                {model.name}
              </h3>


              <div className="mt-5">
                <p className="text-gray-400">
                  Last Closing Price
                </p>

                <p className="text-xl font-semibold">
                  {formatPrice(
                    prediction.last_close
                  )}
                </p>
              </div>


              <div className="mt-4">
                <p className="text-gray-400">
                  Predicted Price
                </p>

                <p className="text-3xl font-bold">
                  {formatPrice(
                    prediction.predicted_price
                  )}
                </p>
              </div>


              <div className="mt-4">
                <p className="text-gray-400">
                  Expected Change
                </p>

                <p
                  className={
                    Number(
                      prediction.predicted_return_percent
                    ) > 0
                      ? "text-green-400 font-semibold"
                      : Number(
                          prediction.predicted_return_percent
                        ) < 0
                      ? "text-red-400 font-semibold"
                      : "text-yellow-400 font-semibold"
                  }
                >
                  {Number(
                    prediction.predicted_return_percent
                  ).toFixed(4)}
                  %
                </p>
              </div>


              <div className="mt-4">
                <p className="text-gray-400">
                  Direction
                </p>

                <p
                  className={`
                    font-semibold
                    ${getDirectionColour(
                      prediction.direction
                    )}
                  `}
                >
                  {prediction.direction}
                </p>
              </div>


              <div className="mt-4">
                <p className="text-gray-400">
                  Direction Probability
                </p>

                <p className="text-blue-400">
                  {formatProbability(
                    prediction.direction_probability
                  )}
                </p>
              </div>


              <div className="mt-5">
                <p className="text-gray-400 mb-2">
                  Recommendation
                </p>

                <p
                  className={`
                    text-lg
                    font-bold
                    ${getRecommendationColour(
                      prediction.recommendation
                    )}
                  `}
                >
                  {prediction.recommendation}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}


export default MultiModelResult;