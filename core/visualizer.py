import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
#from mpl_toolkits.mplot3d import Axes3D


# =====================================================
#  Visualizer
# =====================================================
class Visualizer:
    def __init__(self, df):
        self.df     = df
                        
    def plot_price(self, axis, ticker):
        axis.plot(self.df.index, self.df["Close"], label="Price")
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
        
        # instance figure with subplots
        if ind_t == "MACD":
            fig, (axis_price, axis_macd, axis_ret) = plt.subplots(3, 1, figsize=(20, 12), gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)
        else:
            fig, (axis_price, axis_ret) = plt.subplots(2, 1, figsize=(20, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
        fig.suptitle(f"{ticker} - Backtest {ind_t} ({','.join(params)})")
        self.plot_price(axis_price, ticker)
        axis_price.set_ylabel("Price")
               
        # plot price and indicator
        if ind_t in ["SMA", "EMA", "WMA"]:
            self.plot_ma(axis_price, ind_t, params)
        elif ind_t == "BB":
            self.plot_bb(axis_price, params)
        elif ind_t == "MACD":
            self.plot_macd(axis_macd)
            axis_macd.set_ylabel("MACD")
            axis_macd.grid(True)
        if "Trade" in self.df.columns:
            entries = self.df[self.df["Trade"] == 1]
            exits   = self.df[self.df["Trade"] == -1]
            axis_price.scatter(entries.index, entries["Close"], marker="^", s=60, color="green", label="Buy")
            axis_price.scatter(exits.index, exits["Close"], marker="v", s=60, color="green", label="Sell")
        axis_price.legend()
        axis_price.grid(True)
        
        # plot returns
        axis_ret.plot(self.df.index, self.df["Cumulative_Market"], label="Buy & Hold")
        axis_ret.plot(self.df.index, self.df["Cumulative_Strategy"], label="Strategy")
        axis_ret.set_ylabel("Return")
        axis_ret.legend()
        axis_ret.grid(True)
        plt.tight_layout()
        plt.savefig(f"data/results/{label}_backtest.png", dpi=300, bbox_inches="tight")
        plt.close()               
        
    def plot_optimization(self, opt_global, opt_local, label):
        ticker, ind_t, *params = label.split("_")
        k     = [d["k"] for d in opt_global]
        score = [d["score"] for d in opt_global]
        T     = [d.get("T") for d in opt_global]
        alpha = [d.get("alpha") for d in opt_global]
        
        n_params    = len(opt_global[0]["params"])
        P           = list(zip(*[d["params"] for d in opt_global]))
        if n_params == 2:
            planes = [(0, 1)]
        else:
            planes = [(i, j) for i in range(n_params) for j in range(i+1, n_params)]
        fig = plt.figure(figsize=(20, 12))
        gs  = GridSpec(1 +(len(planes)+1)//2, 2, figure=fig)
        axes = []
        axes.append(fig.add_subplot(gs[0, 0]))
        axes.append(fig.add_subplot(gs[0, 1]))  
              
        # optimization convergence
        axes[0].plot(k, score, color='tab:blue')
        axes[0].set_xlabel("Iteration")
        axes[0].set_ylabel("Score")
        axes[0].set_title(f"{ticker} - Optimization convergence {ind_t}")
        axes[0].grid(True)

        # alpha evolution
        axes[1].plot(k, alpha, label=r"$\alpha$", color='tab:green')
        if any(T_i is not None for T_i in T):
            # temperature evolution
            axes[1].plot(k, T, label="T", color='tab:orange')
        axes[1].set_xlabel("Iteration")
        axes[1].set_ylabel("Value")
        axes[1].set_title(f"{ticker} - Parameters evolution {ind_t}")
        axes[1].legend()
        axes[1].grid(True)

        # heatmap            
        axes_heat = []
        for idx, (i, j) in enumerate(planes):
            ax = fig.add_subplot(gs[1+idx//2, idx%2])
            axes_heat.append(ax)
            
            p1 = P[i]
            p2 = P[j]
            sc = ax.hexbin(p1, p2, C=score, gridsize=10, reduce_C_function=max, cmap="viridis")
            ax.set_xlabel(f"x_{i+1}")
            ax.set_ylabel(f"x_{j+1}")
            ax.set_title(f"{ticker} - Score heatmap {ind_t} (x{i+1}, x{j+1})")
            
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        fig.colorbar(sc, ax=axes_heat, fraction=0.03, pad=0.04, label="Score")
        plt.savefig(f"data/results/{ticker}_{ind_t}_optimization.png", dpi=300)
        plt.close()
        
        # optimization space
        score_local = [d["score"] for d in opt_local]
        if n_params == 2:
            fig, axis = plt.subplots(figsize=(12, 12))
            p1    = [d["params"][0] for d in opt_local]
            p2    = [d["params"][1] for d in opt_local]
            sc    = axis.scatter(p1, p2, c=score_local, cmap="viridis")
            
            axis.set_xlabel("x₁")
            axis.set_ylabel("x₂")
            axis.set_title("Space exploration")
            axis.grid(True)
            fig.colorbar(sc, ax=axis, label="Score")
            
        elif n_params == 3:
            fig = plt.figure(figsize=(12, 12))
            ax3d = fig.add_subplot(111, projection="3d")
            ax3d.set_box_aspect((1, 1, 0.8))
            ax3d.view_init(elev=20, azim=45)
            p1 = [d["params"][0] for d in opt_local]
            p2 = [d["params"][1] for d in opt_local]
            p3 = [d["params"][2] for d in opt_local]
            sc = ax3d.scatter(p1, p2, p3, c=score_local, cmap="viridis")
            
            ax3d.set_xlabel("x₁")
            ax3d.set_ylabel("x₂")
            ax3d.set_zlabel("x₃")
            ax3d.set_title("Space exploration")
            fig.colorbar(sc, ax=ax3d, fraction=0.03, pad=0.04, label="Score")  
            
        else:
            fig = plt.figure(figsize=(20, 12))
                 
        plt.savefig(f"data/results/{ticker}_{ind_t}_exploration.png", dpi=300)
        plt.close()