import { useEffect, useState } from "react";

import ModelPerformance from "../components/ModelPerformance";
import PredictionChart from "../components/PredictionChart";
import AccuracyChart from "../components/AccuracyChart";
import TrainingLossChart from "../components/TrainingLossChart";
import ModelComparisonTable from "../components/ModelComparisonTable";

import { getAnalytics } from "../services/predictionService";


const STOCKS = [
  "AZN.L",
  "BLND.L",
  "BP.L",
  "CCC.L",
  "GSK.L",
  "LAND.L",
  "SGE.L",
  "SHEL.L",
  "TSCO.L",
  "ULVR.L"
];


function Analytics() {
  const [selectedStock, setSelectedStock] = useState("AZN.L");
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        setLoading(true);
        setError("");

        const data = await getAnalytics(
          selectedStock,
          30
        );

        setAnalyticsData(data);
      } catch (requestError) {
        setError(
          requestError.message ||
          "Failed to load analytics data."
        );
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, [selectedStock]);


  return (
    <div className="bg-slate-950 min-h-screen p-8 text-white">
      <div className="flex flex-col gap-4 mb-8 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Analytics Dashboard
          </h1>

          <p className="text-slate-400 mt-2">
            Real model evaluation results and test predictions
          </p>
        </div>


        <div className="w-full md:w-52">
          <label
            htmlFor="analytics-stock"
            className="block text-sm text-slate-400 mb-2"
          >
            Select stock
          </label>

          <select
            id="analytics-stock"
            value={selectedStock}
            onChange={(event) =>
              setSelectedStock(event.target.value)
            }
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none focus:border-blue-500"
          >
            {STOCKS.map((stock) => (
              <option
                key={stock}
                value={stock}
              >
                {stock}
              </option>
            ))}
          </select>
        </div>
      </div>


      {loading && (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <p className="text-slate-300">
            Loading analytics data...
          </p>
        </div>
      )}


      {!loading && error && (
        <div className="rounded-xl border border-red-800 bg-red-950/40 p-6">
          <p className="font-semibold text-red-300">
            Unable to load analytics
          </p>

          <p className="mt-2 text-red-200">
            {error}
          </p>
        </div>
      )}


      {!loading && !error && analyticsData && (
        <div className="space-y-8">
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">
              Best performing model
            </p>

            <h2 className="mt-2 text-2xl font-bold text-emerald-400">
              {analyticsData.best_model?.name || "Not available"}
            </h2>

            <p className="mt-2 text-sm text-slate-400">
              Selected using the lowest RMSE value
            </p>
          </div>


          <ModelPerformance
            models={analyticsData.models}
            comparison={analyticsData.comparison}
          />


          <PredictionChart
            models={analyticsData.models}
            ticker={analyticsData.ticker}
          />


          <AccuracyChart
            comparison={analyticsData.comparison}
          />

          <ModelComparisonTable
            comparison={analyticsData.comparison}
          />

          <TrainingLossChart
            trainingHistory={analyticsData.training_history}
          />
        </div>
      )}
    </div>
  );
}


export default Analytics;