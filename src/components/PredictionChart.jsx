import { useMemo, useState } from "react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts";


const MODEL_OPTIONS = [
  {
    key: "lstm",
    label: "LSTM"
  },
  {
    key: "cnn_lstm",
    label: "CNN/LSTM"
  },
  {
    key: "transfer_learning",
    label: "Chronos-2"
  }
];


function PredictionChart({
  models = {},
  ticker = ""
}) {
  const availableModels = useMemo(
    () =>
      MODEL_OPTIONS.filter(
        (model) =>
          models?.[model.key]?.predictions?.length > 0
      ),
    [models]
  );


  const [selectedModel, setSelectedModel] = useState(
    availableModels[0]?.key || "lstm"
  );


  const activeModel =
    availableModels.find(
      (model) => model.key === selectedModel
    ) || availableModels[0];


  if (!activeModel) {
    return (
      <div className="bg-slate-800 rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-4">
          Actual vs Predicted Price
        </h2>

        <p className="text-slate-400">
          No prediction data is available for this stock.
        </p>
      </div>
    );
  }


  const chartData =
    models[activeModel.key].predictions.map(
      (prediction) => ({
        date:
          prediction.display_date ||
          prediction.date,
        actual: Number(prediction.actual),
        predicted: Number(prediction.predicted)
      })
    );


  return (
    <div className="bg-slate-800 rounded-xl p-6">
      <div className="flex flex-col gap-4 mb-6 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold">
            Actual vs Predicted Price
          </h2>

          <p className="text-slate-400 mt-2">
            {activeModel.label} test predictions for{" "}
            {ticker}
          </p>
        </div>


        <div className="flex flex-wrap gap-2">
          {availableModels.map((model) => {
            const isActive =
              model.key === activeModel.key;

            return (
              <button
                key={model.key}
                type="button"
                onClick={() =>
                  setSelectedModel(model.key)
                }
                className={`
                  rounded-lg
                  px-4
                  py-2
                  text-sm
                  font-semibold
                  transition
                  ${
                    isActive
                      ? "bg-blue-600 text-white"
                      : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                  }
                `}
              >
                {model.label}
              </button>
            );
          })}
        </div>
      </div>


      <ResponsiveContainer
        width="100%"
        height={350}
      >
        <LineChart
          data={chartData}
          margin={{
            top: 10,
            right: 20,
            left: 10,
            bottom: 20
          }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#475569"
          />

          <XAxis
            dataKey="date"
            tick={{
              fill: "#cbd5e1",
              fontSize: 12
            }}
            minTickGap={20}
          />

          <YAxis
            tick={{
              fill: "#cbd5e1",
              fontSize: 12
            }}
            domain={["auto", "auto"]}
            tickFormatter={(value) =>
              Number(value).toFixed(0)
            }
          />

          <Tooltip
            contentStyle={{
              backgroundColor: "#0f172a",
              border: "1px solid #475569",
              borderRadius: "8px"
            }}
            labelStyle={{
              color: "#ffffff"
            }}
            formatter={(value, name) => [
              Number(value).toFixed(2),
              name === "actual"
                ? "Actual Price"
                : "Predicted Price"
            ]}
          />

          <Legend />

          <Line
            type="monotone"
            dataKey="actual"
            name="Actual Price"
            stroke="#22c55e"
            strokeWidth={3}
            dot={false}
            activeDot={{
              r: 5
            }}
          />

          <Line
            type="monotone"
            dataKey="predicted"
            name="Predicted Price"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={false}
            activeDot={{
              r: 5
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}


export default PredictionChart;