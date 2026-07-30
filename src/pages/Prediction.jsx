import { useState } from "react";

import MultiModelResult from "../components/MultiModelResult";
import RecommendationCard from "../components/RecommendationCard";
import { getPrediction } from "../services/predictionService";


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


function Prediction() {
  const [stock, setStock] = useState("AZN.L");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const handlePredict = async () => {
    try {
      setLoading(true);
      setError("");
      setResult(null);

      const data = await getPrediction(stock);

      console.log(
        "Prediction API response:",
        data
      );

      setResult(data);
    } catch (requestError) {
      console.error(
        "Prediction request failed:",
        requestError
      );

      setError(
        requestError.message ||
        "Prediction failed. Please check that the backend server is running."
      );
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="flex-1 bg-slate-950 min-h-screen p-8 text-white">
      <h1 className="text-3xl font-bold mb-8">
        AI Stock Prediction
      </h1>

      <div className="bg-slate-800 rounded-xl p-8">
        <div className="mb-6">
          <label
            htmlFor="stock-select"
            className="block mb-2 font-semibold"
          >
            Select UK Stock
          </label>

          <select
            id="stock-select"
            className="
              w-full
              p-3
              rounded-lg
              bg-slate-700
              border
              border-slate-600
              text-white
              outline-none
              focus:border-blue-500
            "
            value={stock}
            onChange={(event) => {
              setStock(event.target.value);
              setResult(null);
              setError("");
            }}
            disabled={loading}
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
        </div>

        <button
          type="button"
          onClick={handlePredict}
          disabled={loading}
          className="
            bg-blue-600
            hover:bg-blue-700
            px-8
            py-3
            rounded-lg
            font-semibold
            disabled:opacity-50
            disabled:cursor-not-allowed
            transition-colors
          "
        >
          {loading
            ? "Running All Models..."
            : "Run Prediction"}
        </button>

        {loading && (
          <div className="mt-6 bg-slate-700 rounded-lg p-4">
            <p className="text-blue-300 font-medium">
              Running LSTM, CNN/LSTM and Chronos-2 predictions...
            </p>

            <p className="text-sm text-slate-300 mt-1">
              Chronos-2 may take slightly longer when running on CPU.
            </p>
          </div>
        )}

        {error && (
          <div
            className="
              mt-6
              bg-red-950
              border
              border-red-700
              text-red-200
              rounded-lg
              p-4
            "
          >
            <p className="font-semibold">
              Prediction error
            </p>

            <p className="mt-1">
              {error}
            </p>

            <p className="text-sm mt-2 text-red-300">
              Make sure FastAPI is running at
              http://127.0.0.1:8000.
            </p>
          </div>
        )}

        {!loading && result && (
          <>
            <MultiModelResult result={result} />

            <RecommendationCard result={result} />
          </>
        )}
      </div>
    </div>
  );
}


export default Prediction;