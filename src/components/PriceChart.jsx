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


function PriceChart({
  data = [],
  predictedPrice = null
}) {
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="w-full h-96 flex items-center justify-center">
        <p className="text-slate-400">
          Historical price data is not available.
        </p>
      </div>
    );
  }


  const chartData = data.map((item) => ({
    date: item.date,
    actual: Number(item.close),
    prediction: null
  }));


  if (
    predictedPrice !== null &&
    chartData.length > 0
  ) {
    const lastHistoricalPoint =
      chartData[chartData.length - 1];

    chartData[chartData.length - 1] = {
      ...lastHistoricalPoint,
      prediction: lastHistoricalPoint.actual
    };

    chartData.push({
      date: "Prediction",
      actual: null,
      prediction: Number(predictedPrice)
    });
  }


  const formatPrice = (value) => {
    const numericValue = Number(value);

    if (!Number.isFinite(numericValue)) {
      return "N/A";
    }

    return new Intl.NumberFormat("en-GB", {
      style: "currency",
      currency: "GBP",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(numericValue / 100);
  };


  return (
    <div className="w-full h-96">
      <ResponsiveContainer
        width="100%"
        height="100%"
      >
        <LineChart
          data={chartData}
          margin={{
            top: 10,
            right: 30,
            left: 20,
            bottom: 10
          }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#475569"
          />

          <XAxis
            dataKey="date"
            stroke="#cbd5e1"
            tick={{
              fill: "#cbd5e1",
              fontSize: 12
            }}
            minTickGap={20}
          />

          <YAxis
            stroke="#cbd5e1"
            tick={{
              fill: "#cbd5e1",
              fontSize: 12
            }}
            tickFormatter={(value) =>
              `£${(
                Number(value) / 100
              ).toFixed(0)}`
            }
            domain={["auto", "auto"]}
          />

          <Tooltip
            formatter={(value, name) => [
              formatPrice(value),
              name === "actual"
                ? "Actual Price"
                : "Predicted Price"
            ]}
            contentStyle={{
              backgroundColor: "#0f172a",
              border: "1px solid #475569",
              borderRadius: "8px",
              color: "#ffffff"
            }}
            labelStyle={{
              color: "#ffffff"
            }}
          />

          <Legend
            formatter={(value) =>
              value === "actual"
                ? "Actual Price"
                : "Predicted Price"
            }
          />

          <Line
            type="monotone"
            dataKey="actual"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 6 }}
            connectNulls={false}
          />

          <Line
            type="monotone"
            dataKey="prediction"
            stroke="#22c55e"
            strokeWidth={3}
            dot={{ r: 5 }}
            activeDot={{ r: 7 }}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}


export default PriceChart;