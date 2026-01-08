import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


# =====================================================
#  Visualizer
# =====================================================
class Visualizer:
    def __init__(self, df):
        self.df     = df
                        
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
        
    def plot_optimization(self, opt_global, opt_local, label):
        ticker, ind_t, *params = label.split("_")
        k     = [d["k"] for d in opt_global]
        score = [d["score"] for d in opt_global]
        T     = [d["T"] for d in opt_global]
        alpha = [d["alpha"] for d in opt_global]
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
        
        # parameter space
        p1    = [d["params"][0] for d in opt_local]
        p2    = [d["params"][1] for d in opt_local]
        score = [d["score"] for d in opt_local]
        sc    = axes[1,1].scatter(p1, p2, c=score, cmap="viridis")
        fig.colorbar(sc, ax=axes[1,1], label="Score")
        axes[1,1].set_xlabel("x_1")
        axes[1,1].set_ylabel("x_2")
        axes[1,1].set_title("Space exploration")
        axes[1,1].grid(True)
        
        #plt.tight_layout()
        plt.savefig(f"data/results/{ticker}_{ind_t}_optimization.png", dpi=300)
        plt.close()
        
        # heatmap
        plt.figure(figsize=(12,6))
        plt.hexbin(p1, p2, C=score, gridsize=10, reduce_C_function=max, cmap="viridis")
        plt.colorbar(label="Score")
        plt.xlabel("x_1")
        plt.ylabel("x_2")
        plt.title(f"{ticker} - Score heatmap {ind_t}")
        plt.savefig(f"data/results/{ticker}_{ind_t}_optimization_heatmap.png", dpi=300)
        plt.close()