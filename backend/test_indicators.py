import yfinance as yf
from app.indicators import add_indicators

df = yf.download(
    "AAPL",
    period="6mo",
    auto_adjust=False,
    progress=False
)

print("Columns before processing:")
print(df.columns)

df = add_indicators(df)

print("\nColumns after processing:")
print(df.columns)

print(df.tail())
