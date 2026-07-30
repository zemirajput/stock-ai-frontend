function TrainingLossChart({ trainingHistory }) {
  const historyAvailable =
    trainingHistory?.available === true;

  if (!historyAvailable) {
    return (
      <div className="bg-slate-800 rounded-xl p-6 mt-8">
        <h2 className="text-2xl font-bold mb-4">
          Model Training Loss
        </h2>

        <div className="rounded-lg border border-slate-700 bg-slate-900 p-5">
          <p className="text-slate-300">
            Real epoch-by-epoch training loss data is not available.
          </p>

          <p className="text-slate-400 mt-3">
            {trainingHistory?.message ||
              "The training history was not exported from the model notebooks."}
          </p>

          {trainingHistory?.note && (
            <p className="text-slate-400 mt-3">
              {trainingHistory.note}
            </p>
          )}
        </div>
      </div>
    );
  }

  return null;
}


export default TrainingLossChart;