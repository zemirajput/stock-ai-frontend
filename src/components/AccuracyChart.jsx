import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from "recharts";


function AccuracyChart({ comparison = [] }) {

  if (!comparison.length) {
    return (
      <div className="bg-slate-800 rounded-xl p-6 mt-8">
        <h2 className="text-2xl font-bold mb-4">
          Model Comparison
        </h2>

        <p className="text-slate-400">
          No comparison data available.
        </p>
      </div>
    );
  }


  const chartData = comparison.map((model) => ({
    model: model.name,
    accuracy: Number(model.direction_accuracy),
    rmse: Number(model.rmse)
  }));


  const highestAccuracy = Math.max(
    ...chartData.map((item) => item.accuracy)
  );


  return (
    <div className="bg-slate-800 rounded-xl p-6 mt-8">

      <h2 className="text-2xl font-bold mb-2">
        Direction Accuracy Comparison
      </h2>

      <p className="text-slate-400 mb-6">
        Comparison using the real evaluation results from the trained models.
      </p>


      <ResponsiveContainer width="100%" height={350}>

        <BarChart
          data={chartData}
          margin={{
            top: 20,
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
            dataKey="model"
            tick={{
              fill: "#CBD5E1"
            }}
          />

          <YAxis
            domain={[45, 55]}
            tick={{
              fill: "#CBD5E1"
            }}
            label={{
              value: "Accuracy (%)",
              angle: -90,
              position: "insideLeft",
              fill: "#CBD5E1"
            }}
          />

          <Tooltip
            formatter={(value) => [
              `${Number(value).toFixed(2)}%`,
              "Direction Accuracy"
            ]}
            contentStyle={{
              backgroundColor: "#0f172a",
              border: "1px solid #475569",
              borderRadius: "8px"
            }}
          />

          <Bar
            dataKey="accuracy"
            radius={[8, 8, 0, 0]}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={index}
                fill={
                  entry.accuracy === highestAccuracy
                    ? "#22c55e"
                    : "#3b82f6"
                }
              />
            ))}
          </Bar>

        </BarChart>

      </ResponsiveContainer>

    </div>
  );
}


export default AccuracyChart;