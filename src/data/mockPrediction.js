const mockPredictions = {


    AAPL: {

        currentPrice: 195.50,

        models: [

            {
                name: "LSTM",
                predictedPrice: 198.20,
                accuracy: 91.5,
                rmse: 0.032,
                mae: 0.021
            },

            {
                name: "CNN/LSTM",
                predictedPrice: 197.80,
                accuracy: 89.7,
                rmse: 0.041,
                mae: 0.030
            },

            {
                name: "Transfer Learning",
                predictedPrice: 198.60,
                accuracy: 93.2,
                rmse: 0.025,
                mae: 0.018
            }

        ]

    },



    MSFT: {

        currentPrice: 450.20,

        models: [

            {
                name: "LSTM",
                predictedPrice: 454.80,
                accuracy: 92.1,
                rmse: 0.029,
                mae: 0.020
            },

            {
                name: "CNN/LSTM",
                predictedPrice: 453.60,
                accuracy: 90.4,
                rmse: 0.035,
                mae: 0.026
            },

            {
                name: "Transfer Learning",
                predictedPrice: 456.10,
                accuracy: 94.0,
                rmse: 0.022,
                mae: 0.015
            }

        ]

    },



    TSLA: {

        currentPrice: 265.40,

        models: [

            {
                name: "LSTM",
                predictedPrice: 270.10,
                accuracy: 90.2,
                rmse: 0.038,
                mae: 0.024
            },

            {
                name: "CNN/LSTM",
                predictedPrice: 268.90,
                accuracy: 88.5,
                rmse: 0.045,
                mae: 0.031
            },

            {
                name: "Transfer Learning",
                predictedPrice: 271.30,
                accuracy: 92.8,
                rmse: 0.028,
                mae: 0.019
            }

        ]

    },



    GOOGL: {

        currentPrice: 175.30,

        models: [

            {
                name: "LSTM",
                predictedPrice: 178.40,
                accuracy: 91.8,
                rmse: 0.031,
                mae: 0.020
            },

            {
                name: "CNN/LSTM",
                predictedPrice: 177.90,
                accuracy: 89.9,
                rmse: 0.039,
                mae: 0.027
            },

            {
                name: "Transfer Learning",
                predictedPrice: 179.20,
                accuracy: 93.5,
                rmse: 0.024,
                mae: 0.017
            }

        ]

    },



    AMZN: {

        currentPrice: 225.50,

        models: [

            {
                name: "LSTM",
                predictedPrice: 228.10,
                accuracy: 91.2,
                rmse: 0.033,
                mae: 0.022
            },

            {
                name: "CNN/LSTM",
                predictedPrice: 227.60,
                accuracy: 89.5,
                rmse: 0.042,
                mae: 0.029
            },

            {
                name: "Transfer Learning",
                predictedPrice: 229.00,
                accuracy: 94.1,
                rmse: 0.023,
                mae: 0.016
            }

        ]

    },



    NVDA: {

        currentPrice: 180.20,

        models: [

            {
                name: "LSTM",
                predictedPrice: 184.50,
                accuracy: 92.0,
                rmse: 0.030,
                mae: 0.019
            },

            {
                name: "CNN/LSTM",
                predictedPrice: 183.80,
                accuracy: 90.1,
                rmse: 0.037,
                mae: 0.025
            },

            {
                name: "Transfer Learning",
                predictedPrice: 185.60,
                accuracy: 94.3,
                rmse: 0.022,
                mae: 0.014
            }

        ]

    }


};


export default mockPredictions;