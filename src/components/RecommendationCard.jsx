function RecommendationCard({ result }) {
  if (
    !result ||
    !result.predictions
  ) {
    return null;
  }


  const predictions = [
    result.predictions.lstm,
    result.predictions.cnn_lstm,
    result.predictions.transfer_learning
  ].filter(Boolean);


  if (predictions.length === 0) {
    return null;
  }


  const formatPrice = (price) => {
    const numericPrice = Number(price);

    if (!Number.isFinite(numericPrice)) {
      return "N/A";
    }

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


  const recommendationCounts = predictions.reduce(
    (counts, prediction) => {
      const recommendation =
        prediction.recommendation || "HOLD";

      counts[recommendation] =
        (counts[recommendation] || 0) + 1;

      return counts;
    },
    {
      BUY: 0,
      SELL: 0,
      HOLD: 0
    }
  );


  let finalRecommendation = "HOLD";

  if (
    recommendationCounts.BUY >
      recommendationCounts.SELL &&
    recommendationCounts.BUY >
      recommendationCounts.HOLD
  ) {
    finalRecommendation = "BUY";
  } else if (
    recommendationCounts.SELL >
      recommendationCounts.BUY &&
    recommendationCounts.SELL >
      recommendationCounts.HOLD
  ) {
    finalRecommendation = "SELL";
  }


  const averagePredictedPrice =
    predictions.reduce(
      (total, prediction) =>
        total +
        Number(
          prediction.predicted_price || 0
        ),
      0
    ) / predictions.length;


  const averageLastClose =
    predictions.reduce(
      (total, prediction) =>
        total +
        Number(
          prediction.last_close || 0
        ),
      0
    ) / predictions.length;


  const averageChange =
    predictions.reduce(
      (total, prediction) =>
        total +
        Number(
          prediction.predicted_return_percent || 0
        ),
      0
    ) / predictions.length;


  const probabilities = predictions
    .map((prediction) =>
      Number(
        prediction.direction_probability
      )
    )
    .filter((probability) =>
      Number.isFinite(probability)
    );


  const averageProbability =
    probabilities.length > 0
      ? probabilities.reduce(
          (total, probability) =>
            total + probability,
          0
        ) / probabilities.length
      : null;


  const agreementCount =
    recommendationCounts[
      finalRecommendation
    ];


  const agreementText =
    finalRecommendation === "HOLD" &&
    recommendationCounts.HOLD === 0
      ? "Models have mixed recommendations"
      : `${agreementCount} of ${predictions.length} models agree`;


  const recommendationStyle = {
    BUY: "bg-green-600",
    SELL: "bg-red-600",
    HOLD: "bg-yellow-600"
  };


  const recommendationIcon = {
    BUY: "🟢",
    SELL: "🔴",
    HOLD: "🟡"
  };


  return (
    <div
      className="
        bg-slate-900
        border
        border-slate-700
        rounded-xl
        p-6
        mt-8
        text-white
      "
    >
      <h2 className="text-2xl font-bold mb-6">
        AI Recommendation
      </h2>


      <div className="space-y-4">
        <p>
          Stock:
          <span className="font-bold ml-2">
            {result.ticker}
          </span>
        </p>


        <p>
          Model Consensus:
          <span className="text-blue-400 font-bold ml-2">
            {agreementText}
          </span>
        </p>


        <p>
          Average Last Price:
          <span className="font-bold ml-2">
            {formatPrice(
              averageLastClose
            )}
          </span>
        </p>


        <p>
          Average Predicted Price:
          <span className="font-bold ml-2">
            {formatPrice(
              averagePredictedPrice
            )}
          </span>
        </p>


        <p>
          Average Expected Change:
          <span
            className={`
              font-bold
              ml-2
              ${
                averageChange > 0
                  ? "text-green-400"
                  : averageChange < 0
                  ? "text-red-400"
                  : "text-yellow-400"
              }
            `}
          >
            {averageChange.toFixed(4)}%
          </span>
        </p>


        <div className="pt-4">
          <span
            className={`
              inline-block
              px-6
              py-3
              rounded-lg
              font-bold
              ${recommendationStyle[
                finalRecommendation
              ]}
            `}
          >
            {
              recommendationIcon[
                finalRecommendation
              ]
            }{" "}
            {finalRecommendation}
          </span>
        </div>


        <p className="text-gray-400 pt-2">
          Average Direction Probability:
          <span className="ml-2 text-white">
            {averageProbability !== null
              ? `${(
                  averageProbability * 100
                ).toFixed(2)}%`
              : "Not available"}
          </span>
        </p>


        <p className="text-sm text-gray-400">
          This recommendation is based on the
          combined output of LSTM, CNN/LSTM and
          Chronos-2.
        </p>
      </div>
    </div>
  );
}


export default RecommendationCard;