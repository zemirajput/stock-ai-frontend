function ModelComparisonTable({ comparison = [] }) {
  if (!comparison.length) {
    return null;
  }

  const bestRmse = Math.min(
    ...comparison.map((model) => Number(model.rmse))
  );

  const bestMae = Math.min(
    ...comparison.map((model) => Number(model.mae))
  );

  const bestMape = Math.min(
    ...comparison.map((model) => Number(model.mape))
  );

  const bestR2 = Math.max(
    ...comparison.map((model) => Number(model.r2))
  );

  const bestAccuracy = Math.max(
    ...comparison.map(
      (model) => Number(model.direction_accuracy)
    )
  );


  const highlightClass = (isBest) =>
    isBest
      ? "font-bold text-emerald-400"
      : "text-slate-300";


  return (
    <div className="bg-slate-800 rounded-xl p-6 mt-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold">
          Model Comparison Summary
        </h2>

        <p className="text-slate-400 mt-2">
          Best values are highlighted in green.
        </p>
      </div>


      <div className="overflow-x-auto">
        <table className="w-full min-w-[850px] text-left">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400">
              <th className="px-4 py-3">
                Model
              </th>

              <th className="px-4 py-3">
                Direction Accuracy
              </th>

              <th className="px-4 py-3">
                RMSE
              </th>

              <th className="px-4 py-3">
                MAE
              </th>

              <th className="px-4 py-3">
                MAPE
              </th>

              <th className="px-4 py-3">
                R²
              </th>
            </tr>
          </thead>


          <tbody>
            {comparison.map((model) => {
              const accuracy = Number(
                model.direction_accuracy
              );

              const rmse = Number(model.rmse);
              const mae = Number(model.mae);
              const mape = Number(model.mape);
              const r2 = Number(model.r2);

              return (
                <tr
                  key={model.key}
                  className="border-b border-slate-700/70 hover:bg-slate-700/40"
                >
                  <td className="px-4 py-4 font-semibold text-white">
                    {model.name}
                  </td>

                  <td
                    className={`px-4 py-4 ${highlightClass(
                      accuracy === bestAccuracy
                    )}`}
                  >
                    {accuracy.toFixed(2)}%
                  </td>

                  <td
                    className={`px-4 py-4 ${highlightClass(
                      rmse === bestRmse
                    )}`}
                  >
                    {rmse.toFixed(4)}
                  </td>

                  <td
                    className={`px-4 py-4 ${highlightClass(
                      mae === bestMae
                    )}`}
                  >
                    {mae.toFixed(4)}
                  </td>

                  <td
                    className={`px-4 py-4 ${highlightClass(
                      mape === bestMape
                    )}`}
                  >
                    {mape.toFixed(4)}%
                  </td>

                  <td
                    className={`px-4 py-4 ${highlightClass(
                      r2 === bestR2
                    )}`}
                  >
                    {r2.toFixed(6)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>


      <div className="mt-5 rounded-lg border border-slate-700 bg-slate-900 p-4">
        <p className="text-sm text-slate-400">
          Lower RMSE, MAE and MAPE values indicate smaller
          prediction errors. Higher R² and direction accuracy
          values indicate better model performance.
        </p>
      </div>
    </div>
  );
}


export default ModelComparisonTable;