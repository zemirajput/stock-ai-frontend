function PredictionResult({ result }) {

    if (!result) return null;

    return (

        <div className="bg-slate-800 rounded-xl p-6 mt-8 text-white shadow-lg">

            <h2 className="text-2xl font-bold mb-6">
                Prediction Result
            </h2>


            <div className="grid grid-cols-2 gap-6">


                <div>
                    <p className="text-gray-400">
                        Stock
                    </p>

                    <p className="text-xl">
                        {result.stock}
                    </p>
                </div>


                <div>
                    <p className="text-gray-400">
                        Model
                    </p>

                    <p className="text-xl">
                        {result.model}
                    </p>
                </div>


                <div>
                    <p className="text-gray-400">
                        Current Price
                    </p>

                    <p className="text-xl">
                        ${result.currentPrice}
                    </p>
                </div>


                <div>
                    <p className="text-gray-400">
                        Predicted Price
                    </p>

                    <p className="text-green-400 text-xl">
                        ${result.predictedPrice}
                    </p>
                </div>


                <div>
                    <p className="text-gray-400">
                        Expected Change
                    </p>

                    <p className="text-blue-400">
                        {result.change}
                    </p>
                </div>


                <div>
                    <p className="text-gray-400">
                        Confidence
                    </p>

                    <p className="text-yellow-400">
                        {result.confidence}
                    </p>
                </div>


            </div>


            <div className="mt-8">

                <span className="bg-green-600 px-4 py-2 rounded-lg">
                    Recommendation: BUY
                </span>

            </div>


        </div>

    );

}


export default PredictionResult;    