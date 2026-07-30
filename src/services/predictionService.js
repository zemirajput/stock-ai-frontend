const API_BASE_URL = "http://127.0.0.1:8000";


const getErrorMessage = async (response) => {
  try {
    const data = await response.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    if (data?.detail?.message) {
      return data.detail.message;
    }

    return "The backend request failed.";
  } catch {
    return "The backend returned an invalid response.";
  }
};


export const getPrediction = async (stock) => {
  const response = await fetch(
    `${API_BASE_URL}/predict`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        ticker: stock,
        model: "all"
      })
    }
  );


  if (!response.ok) {
    throw new Error(
      await getErrorMessage(response)
    );
  }


  return response.json();
};


export const getStockHistory = async (
  stock,
  days = 60
) => {
  const response = await fetch(
    `${API_BASE_URL}/history/${encodeURIComponent(
      stock
    )}?days=${days}`
  );


  if (!response.ok) {
    throw new Error(
      await getErrorMessage(response)
    );
  }


  const data = await response.json();

  return data.history || [];
};


export const getAnalytics = async (
  stock = "AZN.L",
  samples = 30
) => {
  const query = new URLSearchParams({
    ticker: stock,
    samples: String(samples)
  });

  const response = await fetch(
    `${API_BASE_URL}/analytics?${query.toString()}`
  );


  if (!response.ok) {
    throw new Error(
      await getErrorMessage(response)
    );
  }


  return response.json();
};