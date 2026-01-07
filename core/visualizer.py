import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================================
#  Visualizer
# =====================================================
class Visualizer:
    def __init__(self, df, folder="data/results"):
        self.df     = df
        self.folder = folder
        
    def clear_folder(self):
        for file in os.listdir(self.folder):
            file_path = os.path.join(self.folder, file)
            if os.path.isfile(file_path) and file != ".gitkeep": os.remove(file_path)
                
    def plot_price(self, axis, ticker):
        axis.plot(self.df.index, self.df["Close"], label=ticker)
        axis.grid(True)
    
    def plot_ma(self, axis, ind_t, params):
        if "Short" in self.df and len(params) >= 1:
            axis.plot(self.df.index, self.df["Short"], label=f"{ind_t}{params[0]}")
        if "Long" in self.df and len(params) == 2:
            axis.plot(self.df.index, self.df["Long"], label=f"{ind_t}{params[1]}")
        if "Long" in self.df and len(params) >= 3:
            axis.plot(self.df.index, self.df["Long"], label=f"{ind_t}{params[1]}")
        if "Med" in self.df and len(params) >= 3:
             axis.plot(self.df.index, self.df["Mid"], label=f"{ind_t}{params[2]}")
    
    def plot_bb(self, axis, params):
        axis.plot(self.df.index, self.df["BB_Mid"], label=f"BB mean {params[0]}")
        axis.plot(self.df.index, self.df["BB_Upper"], color='r', label=f"BB std {params[1]}")
        axis.plot(self.df.index, self.df["BB_Lower"], color='r')
        
    def plot_macd(self, axis):
        axis.plot(self.df.index, self.df["MACD"], label="MACD")
        axis.plot(self.df.index, self.df["MACD_Signal"], label="MACD_Signal")
        axis.bar(self.df.index, self.df["MACD_Histogram"], color='r', label="Histogram", alpha=0.4)
        axis.axhline(0, linewidth=1)
        axis.grid(True)

    def plot_results(self, label):
        ticker, ind_t, *params = label.split("_")

        # plot price and indicator
        if ind_t in ["SMA", "EMA", "WMA"]:
            fig, axis = plt.subplots(figsize=(12,6))
            self.plot_price(axis, ticker)
            self.plot_ma(axis, ind_t, params)
            axis.set_title(f"{ticker} - Price")
            axis.legend()
        elif ind_t == "BB":
            fig, axis = plt.subplots(figsize=(12,6))
            self.plot_price(axis, ticker)
            self.plot_bb(axis, params)
            axis.set_title(f"{ticker} - Price")
            axis.legend()
        elif ind_t == "MACD":
            fig, (axis_price, axis_macd) = plt.subplots(2, 1, figsize=(12,8), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
            self.plot_price(axis_price, ticker)
            axis_price.set_title(f"{ticker} - Price")
            self.plot_macd(axis_macd)
        plt.tight_layout()
        plt.savefig(f"data/results/{label}.png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # plot returns
        plt.figure(figsize=(12,6))
        plt.plot(self.df.index, self.df["Cumulative_Market"], label="Buy & Hold")
        plt.plot(self.df.index, self.df["Cumulative_Strategy"], label="Strategy")
        plt.title(f"{ticker} - Backtest {ind_t} {'/'.join(params)}")
        plt.ylabel("Return")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"data/results/{label}_backtest.png", dpi=300, bbox_inches="tight")
        plt.close()
        
    def plot_optimization(self, data_opt, label):
        ticker, ind_t, *params = label.split("_")
        k     = [d["k"] for d in data_opt]
        score = [d["score"] for d in data_opt]
        T     = [d["T"] for d in data_opt]
        alpha = [d["alpha"] for d in data_opt]
        fig, axes = plt.subplots(2, 2, figsize=(12, 12))
        
        # optimization convergence
        axes[0,0].plot(k, score, color='tab:blue')
        axes[0,0].set_xlabel("Iteration")
        axes[0,0].set_ylabel("Score")
        axes[0,0].set_title(f"{ticker} - Optimization convergence {ind_t}")
        axes[0,0].grid(True)

        # temperature evolution
        axes[0,1].plot(k, T, color='tab:orange')
        axes[0,1].set_xlabel("Iteration")
        axes[0,1].set_ylabel("Temperature")
        axes[0,1].set_title(f"{ticker} - Temperature decay {ind_t}")
        axes[0,1].grid(True)
        
        # alpha evolution
        axes[1,0].plot(k, alpha, color='tab:green')
        axes[1,0].set_xlabel("Iteration")
        axes[1,0].set_ylabel("Step size")
        axes[1,0].set_title(f"{ticker} - Step size decay {ind_t}")
        axes[1,0].grid(True)
        
        # heatmap
        # k_vals = sorted(set(k))
        # T_vals = sorted(set(T))
        # matrix = []
        # for T in T_vals:
        #     row = []
            
        #     for k in k_vals:
        #         matching = [d["score"] for d in data_opt if d["k"]==k and d["T"]==T]
        #         row.append(matching[0] if matching else 0)
        #     matrix.append(row)
            
        # sns.heatmap(matrix, annot=True, fmt=".2f", cmap="YlGnBu")
        # axes[1,1].set_xlabel("Iteration")
        # axes[1,1].set_ylabel("Temperature")
        # axes[1,1].set_title(f"{ticker} - Score heatmap {ind_t}")

        plt.tight_layout()
        plt.savefig(f"data/results/{ticker}_{ind_t}_optimization.png", dpi=300)
        plt.close()