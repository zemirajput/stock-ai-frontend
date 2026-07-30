import pandas as pd
import ta


def add_indicators(df):

    # Make a copy
    df = df.copy()

    # Flatten MultiIndex columns (new yfinance versions)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Convert OHLCV columns to Series if needed
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            if isinstance(df[col], pd.DataFrame):
                df[col] = df[col].iloc[:, 0]

    # Moving averages
    df["SMA_10"] = ta.trend.sma_indicator(df["Close"], window=10)
    df["SMA_50"] = ta.trend.sma_indicator(df["Close"], window=50)

    df["EMA_10"] = ta.trend.ema_indicator(df["Close"], window=10)
    df["EMA_50"] = ta.trend.ema_indicator(df["Close"], window=50)

    # RSI
    df["RSI_14"] = ta.momentum.rsi(df["Close"], window=14)

    # MACD
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()
    df["MACD_Hist"] = macd.macd_diff()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df["Close"])
    df["Bollinger_Mid"] = bb.bollinger_mavg()
    df["Bollinger_Upper"] = bb.bollinger_hband()
    df["Bollinger_Lower"] = bb.bollinger_lband()

    # ATR
    atr = ta.volatility.AverageTrueRange(
        high=df["High"],
        low=df["Low"],
        close=df["Close"]
    )
    df["ATR_14"] = atr.average_true_range()

    # OBV
    df["OBV"] = ta.volume.on_balance_volume(
        close=df["Close"],
        volume=df["Volume"]
    )

    # Returns
    df["Daily_Return"] = df["Close"].pct_change(fill_method=None)
    df["Volatility_10"] = df["Daily_Return"].rolling(10).std()
    df["Momentum_10"] = df["Close"] - df["Close"].shift(10)

    df["Return_Lag_1"] = df["Daily_Return"].shift(1)
    df["Return_Lag_2"] = df["Daily_Return"].shift(2)
    df["Return_Lag_3"] = df["Daily_Return"].shift(3)

    return df