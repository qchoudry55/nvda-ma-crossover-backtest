#IMPORT ALL REQUIRED EXTERNAL LIBRARIES (INITIALLY VIA PIP)
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

#IMPORT RAW DATA FOR NVIDIA VIA YFINANCE
data = yf.download("NVDA", start = "2018-01-01", end = "2024-06-01")
data["MA50"] = data["Close"].rolling(window=50).mean()
data["MA200"] = data["Close"].rolling(window=200).mean()
data["Signal"] = data["MA50"] > data["MA200"]

#MA AND CROSSOVER SIGNAL VIA PANDAS
data["PreviousSignal"] = data["Signal"].shift(1).fillna(False).astype(bool)
cond1 = data["Signal"]
cond2 = ~data["PreviousSignal"]
data["Buy"] = (cond1) & (cond2)
data["Sell"] = (~cond1) & (~cond2)

#BUY/SELL SIGNALS FROM CROSSOVER
data.loc[data["Buy"] == True, "Position"] = 1
data.loc[data["Sell"] == True, "Position"] = 0
data["Position"] = data["Position"].ffill()
data["Position"] = data["Position"].fillna(0)

#DAILY RETURNS
data["MarketRet"] = data["Close"].pct_change()
data["StratRet"] = data["Position"].shift(1) * data["MarketRet"]

#CUM GROWTH
data["StratGrth"] = (1 + data["StratRet"]).cumprod()
data["MarketGrth"] = (1 + data["MarketRet"]).cumprod()

#MAX DRAWDOWN
data["RnningPeak"] = data["StratGrth"].cummax()
data["Drawdown"] = (data["StratGrth"] - data["RnningPeak"]) / data["RnningPeak"]
max_drawdown_pct = data["Drawdown"].min() * 100

#SUMMARIES FIGURES TO BE PRINTED FOR USER
final_strat_grth = data["StratGrth"].iloc[-1]
final_market_grth = data["MarketGrth"].iloc[-1]
strat_ret_pct = (final_strat_grth - 1) * 100
market_ret_pct = (final_market_grth - 1) * 100
no_of_buy_signals = data["Buy"].sum()

print(f"Strategy return: {strat_ret_pct:.2f}%")
print(f"Market return: {market_ret_pct:.2f}%")
print(f"Maximum drawdown: {max_drawdown_pct:.2f}%")
print(f"Number of buy signals: {no_of_buy_signals}")

#PLOT RAW CLOSING PRICE VIA MATPLOTLIB
plt.plot(data["Close"])
plt.title("NVIDIA (NVDA) Closing Price, 2018-2024")
plt.xlabel("Date")
plt.ylabel("Closing Price (USD)")
plt.savefig("nvda_closing_price.png")
plt.show()

#PLOT MA STRATEGY VS BUY-AND-HOLD ON ONE GRAPH TO SHOW HOW STRATEGIES ARE DIFFERENT
plt.plot(data["StratGrth"], label="Moving Average Strategy")
plt.plot(data["MarketGrth"], label="Buy and Hold")
plt.legend()
plt.title("NVDA Moving Average Strategy vs Buy and Hold, 2018-2024")
plt.xlabel("Date")
plt.ylabel("Growth of £1 Invested")
plt.savefig("strategy_vs_buyhold.png")
plt.show()