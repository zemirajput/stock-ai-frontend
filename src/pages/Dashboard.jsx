import { useState } from "react";

import PriceChart from "../components/PriceChart";

import {
  getPrediction,
  getStockHistory
} from "../services/predictionService";


const stocks = [
  {
    ticker: "AZN.L",
    name: "AstraZeneca"
  },
  {
    ticker: "BLND.L",
    name: "British Land"
  },
  {
    ticker: "BP.L",
    name: "BP"
  },
  {
    ticker: "CCC.L",
    name: "Computacenter"
  },
  {
    ticker: "GSK.L",
    name: "GSK"
  },
  {
    ticker: "LAND.L",
    name: "Land Securities"
  },
  {
    ticker: "SGE.L",
    name: "Sage Group"
  },
  {
    ticker: "SHEL.L",
    name: "Shell"
  },
  {
    ticker: "TSCO.L",
    name: "Tesco"
  },
  {
    ticker: "ULVR.L",
    name: "Unilever"
  }
];


function Dashboard() {
  const [stock, setStock] = useState("AZN.L");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const formatPrice = (price) => {
    const numericPrice = Number(price);

    if (!Number.isFinite(numericPrice)) {
      return "N/A";
    }

    const priceInPounds = numericPrice / 100;

    return new Intl.NumberFormat("en-GB", {
      style: "currency",
      currency: "GBP",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(priceInPounds);
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


  const getChangeColour = (change) => {
    const numericChange = Number(change);

    if (numericChange > 0) {
      return "text-green-400";
    }

    if (numericChange < 0) {
      return "text-red-400";
    }

    return "text-yellow-400";
  };


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


  const getRecommendationBackground = (
    recommendation
  ) => {
    if (recommendation === "BUY") {
      return "bg-green-600";
    }

    if (recommendation === "SELL") {
      return "bg-red-600";
    }

    return "bg-yellow-600";
  };


  const handlePrediction = async () => {
    try {
      setLoading(true);
      setError("");
      setResult(null);
      setHistory([]);

      const [
        predictionData,
        historyData
      ] = await Promise.all([
        getPrediction(stock),
        getStockHistory(stock, 60)
      ]);

      console.log(
        "Dashboard prediction response:",
        predictionData
      );

      console.log(
        "Dashboard history response:",
        historyData
      );

      setResult(predictionData);
      setHistory(historyData);
    } catch (requestError) {
      console.error(
        "Dashboard request error:",
        requestError
      );

      setError(
        requestError.message ||
        "Unable to load stock information."
      );
    } finally {
      setLoading(false);
    }
  };


  const predictions = result?.predictions
    ? [
        result.predictions.lstm,
        result.predictions.cnn_lstm,
        result.predictions.transfer_learning
      ].filter(Boolean)
    : [];


  const modelCards = result?.predictions
    ? [
        {
          key: "lstm",
          name: "LSTM",
          prediction: result.predictions.lstm
        },
        {
          key: "cnn_lstm",
          name: "CNN/LSTM",
          prediction:
            result.predictions.cnn_lstm
        },
        {
          key: "transfer_learning",
          name: "Transfer Learning",
          prediction:
            result.predictions.transfer_learning
        }
      ]
    : [];


  const averageCurrentPrice =
    predictions.length > 0
      ? predictions.reduce(
          (total, prediction) =>
            total +
            Number(
              prediction.last_close || 0
            ),
          0
        ) / predictions.length
      : null;


  const averagePredictedPrice =
    predictions.length > 0
      ? predictions.reduce(
          (total, prediction) =>
            total +
            Number(
              prediction.predicted_price || 0
            ),
          0
        ) / predictions.length
      : null;


  const averageChange =
    predictions.length > 0
      ? predictions.reduce(
          (total, prediction) =>
            total +
            Number(
              prediction.predicted_return_percent || 0
            ),
          0
        ) / predictions.length
      : null;


  const recommendationCounts =
    predictions.reduce(
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


  return (
    <div className="flex-1 bg-slate-950 min-h-screen p-8">
      <h1
        className="
          text-3xl
          font-bold
          text-white
          mb-8
        "
      >
        Stock Market Prediction Dashboard
      </h1>


      <div
        className="
          bg-slate-800
          rounded-xl
          p-6
          border
          border-slate-700
        "
      >
        <label
          htmlFor="dashboard-stock"
          className="
            block
            text-white
            font-semibold
            mb-2
          "
        >
          Select UK Stock
        </label>


        <div
          className="
            flex
            flex-col
            md:flex-row
            gap-4
          "
        >
          <select
            id="dashboard-stock"
            value={stock}
            disabled={loading}
            onChange={(event) => {
              setStock(event.target.value);
              setResult(null);
              setHistory([]);
              setError("");
            }}
            className="
              flex-1
              bg-slate-700
              text-white
              p-3
              rounded-lg
              border
              border-slate-600
              outline-none
              focus:border-blue-500
            "
          >
            {stocks.map((item) => (
              <option
                key={item.ticker}
                value={item.ticker}
              >
                {item.name} ({item.ticker})
              </option>
            ))}
          </select>


          <button
            type="button"
            disabled={loading}
            onClick={handlePrediction}
            className="
              bg-blue-600
              hover:bg-blue-700
              text-white
              font-semibold
              px-8
              py-3
              rounded-lg
              disabled:opacity-50
              disabled:cursor-not-allowed
              transition-colors
            "
          >
            {loading
              ? "Running Models..."
              : "Analyse Stock"}
          </button>
        </div>
      </div>


      {loading && (
        <div
          className="
            bg-slate-800
            border
            border-blue-700
            rounded-xl
            p-5
            mt-6
            text-white
          "
        >
          <p className="text-blue-300 font-semibold">
            Generating predictions...
          </p>

          <p className="text-slate-400 text-sm mt-1">
            Running LSTM, CNN/LSTM and Chronos-2.
            This may take some time on CPU.
          </p>
        </div>
      )}


      {error && (
        <div
          className="
            bg-red-950
            border
            border-red-700
            rounded-xl
            p-5
            mt-6
            text-red-200
          "
        >
          <p className="font-semibold">
            Request failed
          </p>

          <p className="mt-1">
            {error}
          </p>

          <p className="text-sm text-red-300 mt-2">
            Make sure FastAPI is running at
            http://127.0.0.1:8000.
          </p>
        </div>
      )}


      {!result && !loading && !error && (
        <div
          className="
            bg-slate-800
            rounded-xl
            p-8
            mt-8
            text-center
            border
            border-slate-700
          "
        >
          <p className="text-slate-300 text-lg">
            Select a stock and click{" "}
            <span className="font-semibold text-white">
              Analyse Stock
            </span>{" "}
            to view real AI predictions.
          </p>
        </div>
      )}


      {result && predictions.length > 0 && (
        <>
          <div
            className="
              grid
              grid-cols-1
              md:grid-cols-2
              xl:grid-cols-4
              gap-6
              mt-8
            "
          >
            <div
              className="
                bg-slate-800
                rounded-xl
                p-6
                border
                border-slate-700
              "
            >
              <p className="text-slate-400">
                Current Price
              </p>

              <p className="text-white text-3xl font-bold mt-2">
                {formatPrice(
                  averageCurrentPrice
                )}
              </p>
            </div>


            <div
              className="
                bg-slate-800
                rounded-xl
                p-6
                border
                border-slate-700
              "
            >
              <p className="text-slate-400">
                Average Predicted Price
              </p>

              <p className="text-white text-3xl font-bold mt-2">
                {formatPrice(
                  averagePredictedPrice
                )}
              </p>
            </div>


            <div
              className="
                bg-slate-800
                rounded-xl
                p-6
                border
                border-slate-700
              "
            >
              <p className="text-slate-400">
                Average Expected Change
              </p>

              <p
                className={`
                  text-3xl
                  font-bold
                  mt-2
                  ${getChangeColour(
                    averageChange
                  )}
                `}
              >
                {Number(
                  averageChange
                ).toFixed(4)}
                %
              </p>
            </div>


            <div
              className="
                bg-slate-800
                rounded-xl
                p-6
                border
                border-slate-700
              "
            >
              <p className="text-slate-400">
                AI Recommendation
              </p>

              <span
                className={`
                  inline-block
                  text-white
                  px-5
                  py-2
                  rounded-lg
                  font-bold
                  mt-3
                  ${getRecommendationBackground(
                    finalRecommendation
                  )}
                `}
              >
                {finalRecommendation}
              </span>
            </div>
          </div>


          <h2
            className="
              text-2xl
              font-bold
              text-white
              mt-10
              mb-6
            "
          >
            Model Predictions
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
            {modelCards.map((model) => {
              const prediction =
                model.prediction;

              if (!prediction) {
                return null;
              }

              return (
                <div
                  key={model.key}
                  className="
                    bg-slate-800
                    rounded-xl
                    p-6
                    text-white
                    border
                    border-slate-700
                    shadow-lg
                  "
                >
                  <h3 className="text-xl font-bold">
                    {model.name}
                  </h3>


                  <div className="mt-5">
                    <p className="text-slate-400">
                      Predicted Price
                    </p>

                    <p className="text-3xl font-bold mt-1">
                      {formatPrice(
                        prediction.predicted_price
                      )}
                    </p>
                  </div>


                  <div className="mt-4">
                    <p className="text-slate-400">
                      Expected Change
                    </p>

                    <p
                      className={`
                        font-semibold
                        ${getChangeColour(
                          prediction
                            .predicted_return_percent
                        )}
                      `}
                    >
                      {Number(
                        prediction
                          .predicted_return_percent
                      ).toFixed(4)}
                      %
                    </p>
                  </div>


                  <div className="mt-4">
                    <p className="text-slate-400">
                      Direction
                    </p>

                    <p className="font-semibold">
                      {prediction.direction}
                    </p>
                  </div>


                  <div className="mt-4">
                    <p className="text-slate-400">
                      Direction Probability
                    </p>

                    <p className="text-blue-400">
                      {formatProbability(
                        prediction
                          .direction_probability
                      )}
                    </p>
                  </div>


                  <div className="mt-4">
                    <p className="text-slate-400">
                      Recommendation
                    </p>

                    <p
                      className={`
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


          <div
            className="
              bg-slate-800
              rounded-xl
              mt-10
              p-8
              text-white
              border
              border-slate-700
            "
          >
            <div
              className="
                flex
                flex-col
                md:flex-row
                md:items-center
                md:justify-between
                gap-3
                mb-6
              "
            >
              <div>
                <h2 className="text-xl font-bold">
                  Stock Price Performance
                </h2>

                <p className="text-slate-400 text-sm mt-1">
                  Last 60 trading days for {stock}
                </p>
              </div>


              <div className="flex items-center gap-5 text-sm">
                <span className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-blue-500" />

                  Historical price
                </span>

                <span className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-green-500" />

                  Average prediction
                </span>
              </div>
            </div>


            <PriceChart
              data={history}
              predictedPrice={
                averagePredictedPrice
              }
            />
          </div>


          <div
            className="
              bg-slate-800
              rounded-xl
              mt-10
              p-8
              text-white
              border
              border-slate-700
            "
          >
            <h2 className="text-xl font-bold">
              Model Information
            </h2>


            <div
              className="
                grid
                grid-cols-1
                md:grid-cols-3
                gap-6
                mt-6
              "
            >
              <div>
                <p className="text-blue-400 font-semibold">
                  LSTM
                </p>

                <p className="text-slate-300 mt-2">
                  Long Short-Term Memory neural
                  network using historical prices
                  and technical indicators.
                </p>
              </div>


              <div>
                <p className="text-blue-400 font-semibold">
                  CNN/LSTM
                </p>

                <p className="text-slate-300 mt-2">
                  Hybrid model combining
                  convolutional feature extraction
                  with sequential LSTM forecasting.
                </p>
              </div>


              <div>
                <p className="text-blue-400 font-semibold">
                  Chronos-2
                </p>

                <p className="text-slate-300 mt-2">
                  Transfer-learning time-series model
                  used to forecast the next closing
                  price.
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}


export default Dashboard;