function ModelPerformance({ comparison = [] }) {
  if (!comparison.length) {
    return (
      <div className="bg-slate-800 rounded-xl p-6">
        <p className="text-slate-400">
          No model performance data available.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-5">
        Model Performance
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {comparison.map((model) => (
          <div
            key={model.key}
            className="bg-slate-800 rounded-xl p-6"
          >
            <h3 className="text-xl font-bold mb-4">
              {model.name}
            </h3>

            <div className="space-y-2">

              <p>
                Direction Accuracy:
                <span className="text-green-400 ml-2">
                  {model.direction_accuracy.toFixed(2)}%
                </span>
              </p>

              <p>
                RMSE:
                <span className="text-blue-400 ml-2">
                  {model.rmse.toFixed(4)}
                </span>
              </p>

              <p>
                MAE:
                <span className="text-yellow-400 ml-2">
                  {model.mae.toFixed(4)}
                </span>
              </p>

              <p>
                MAPE:
                <span className="text-pink-400 ml-2">
                  {model.mape.toFixed(4)}%
                </span>
              </p>

              <p>
                R²:
                <span className="text-cyan-400 ml-2">
                  {model.r2.toFixed(6)}
                </span>
              </p>

            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ModelPerformance;