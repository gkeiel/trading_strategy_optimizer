import json


# =====================================================
#  Backtester
# =====================================================
class Backtester:
    def __init__(self, df):
        self.df = df.copy()

    def run_strategy(self, indicator):
        try:
            df     = self.df
            ind_t  = indicator["ind_t"]
            params = indicator["ind_p"]   
    
            # generate buy/sell signals
            df["Signal"] = 0
            if ind_t in ["SMA", "EMA", "WMA"]:
                if len(params) == 1:
                    # 1 MA crossover
                    df.loc[df["Close"] > df["Short"], "Signal"] = 1         # buy signal (MA)
                    df.loc[df["Close"] < df["Short"], "Signal"] = -1        # sell signal (MA)
                elif len(params) == 2:
                    # 2 MAs crossover
                    df.loc[df["Short"] > df["Long"], "Signal"] = 1          
                    df.loc[df["Short"] < df["Long"], "Signal"] = -1         
                elif len(params) == 3:
                    # 3 MAs crossover
                    df.loc[(df["Short"] > df["Med"]) & (df["Med"] > df["Long"]), "Signal"] = 1
                    df.loc[(df["Short"] < df["Med"]) & (df["Med"] < df["Long"]), "Signal"] = -1
            elif ind_t == "BB":
                df.loc[df["Close"] < df["BB_Lower"], "Signal"] = 1          # buy signal (BB)
                df.loc[df["Close"] > df["BB_Upper"], "Signal"] = -1         # seel signal (BB)
            elif ind_t == "MACD":
                df.loc[df["MACD"] > df["MACD_Signal"], "Signal"] = 1        # buy signal (MACD)
                df.loc[df["MACD"] < df["MACD_Signal"], "Signal"] = -1       # sell signal (MACD)
            
            df["Signal_Length"] = df["Signal"].groupby((df["Signal"] != df["Signal"].shift()).cumsum()).cumcount() +1   # consecutive samples of same signal (signal length)
            df.loc[df["Signal"] == 0, "Signal_Length"] = 0                                                              # length is zero while there is no signal
            df["Volume_MA"] = df["Volume"].rolling(window=10).mean()                                                    # volume MA
            df["Volume_Strength"] = (df["Volume"] -df["Volume_MA"])/df["Volume_MA"]                                     # volume strenght

            # simulate execution (backtest)
            df["Position"] = df["Signal"].shift(1)                      # simulate position (using previous sample)
            # df.loc[df["Position"] == -1, "Position"] = 0                # comment if also desired selling operations  
            df["Trade"] = df["Position"].diff().abs()                   # simulate trade
            df["Entry_Price"] = df["Close"].where(df["Trade"] == 1)     # entry price
            df["Entry_Price"] = df["Entry_Price"].ffill()
            df["Return"] = df["Close"].pct_change()                     # asset percentage variation (in relation to previous sample)
            df["Strategy"] = df["Position"]*df["Return"]                # return of the strategy
            df["Strategy"] = df["Strategy"].fillna(0.00001)
            
            # compare benchmark vs current strategy
            df["Cumulative_Market"] = (1 +df["Return"]).cumprod()       # cumulative return buy & hold strategy
            df["Cumulative_Strategy"] = (1 +df["Strategy"]).cumprod()   # cumulative return current strategy
            df["Cumulative_Trades"] = df["Trade"].cumsum()              # cumulative number of trades
        
            # calculate drawdown
            df["Drawdown"] = (df["Cumulative_Strategy"] -df["Cumulative_Strategy"].cummax())/df["Cumulative_Strategy"].cummax()
            
        
        except KeyError as err:
            raise KeyError(f"Required column missing in backtest: {err}")
        except ZeroDivisionError as err:
            raise RuntimeError("Division by zero in backtest calculations.") from err
        except Exception as err:
            raise RuntimeError(f"Error in backtest run_strategy: {err}") from err
        return df