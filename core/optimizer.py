from .indicator import Indicator
from .backtester import Backtester
from .strategies import Strategies
import math, random, copy


# =====================================================
#  Optimizer
# =====================================================
class Optimizer:
    def __init__(self, df, search_space):
        self.df       = df
        self.space    = search_space
        self.data     = []
        self.data_opt = []

    def evaluate(self, indicator):
        df = self.df.copy()
        
        # setup indicator
        df = Indicator(indicator).setup_indicator(df)

        # run backtest
        backtest = Backtester(df)
        df       = backtest.run_strategy(indicator)
        
        # compute metrics
        metrics = {
            "Return_Market": df["Cumulative_Market"].iloc[-1],
            "Return_Strategy": df["Cumulative_Strategy"].iloc[-1],
            "Trades": df["Cumulative_Trades"].iloc[-1]//2,
            "Sharpe": df["Strategy"].mean() / df["Strategy"].std()*pow(len(df), 0.5),
            "Max_Drawdown": abs(df["Drawdown"].min()),
        }
        
        # compute score
        score = Strategies().compute_score(metrics)
        
        # append to data
        self.data.append({"indicator": indicator, "df": df, "metrics": metrics, "score": score})
        return score, df, metrics
    
    def search(self):
        start_indicator = {
            "ind_t": self.space["ind_t"],
            "ind_p": [
                int((p["min"] +p["max"])/2)
                for p in self.space["params"]
            ]
        }
        
        self.log   = open(f"data/results/{start_indicator['ind_t']}_log.txt", "w")
        best_params, best_score = self.simulated_annealing(start_indicator=start_indicator)
        self.log.close()
        return self.data
    
    def random_neighbor(self, indicator, alpha):
        x = copy.deepcopy(indicator)

        for i, val in enumerate(x["ind_p"]):
            pmin  = self.space["params"][i]["min"]
            pmax  = self.space["params"][i]["max"]
            step  = max(1, round(alpha*(pmax -pmin)/5))
            new_v = val +random.randint(-step, step)
            x["ind_p"][i] = max(pmin, min(pmax, new_v))
                    
        if x["ind_t"] == "MACD":
            fast, slow, signal = x["ind_p"]
            if fast   >= slow: fast   = slow -1
            if signal >= slow: signal = slow -1
            
            fast   = max(self.space["params"][0]["min"], fast)
            signal = max(self.space["params"][2]["min"], signal)
            x["ind_p"] = [fast, slow, signal]

        return x

    def hill_climbing(self, start_indicator, alpha=1, n=2, k_max=60):
        x_i       = start_indicator
        f_i, _, _ = self.evaluate(x_i)
        k         = 0
        
        while k < k_max:
            k = k +1
            
            for _ in range(n):
                x_j       = self.random_neighbor(x_i, alpha)
                f_j, _, _ = self.evaluate(x_j)

                if f_j > f_i:
                    x_i = x_j
                    f_i = f_j

        return x_i, f_i
    
    def simulated_annealing(self, start_indicator, alpha=1, beta=0.95, n=2, k_max=60):
        x_i       = start_indicator
        f_i, _, _ = self.evaluate(x_i)
        T         = 1
        k         = 0
        
        while k < k_max:
            k = k +1
            
            for _ in range(n):
                x_j       = self.random_neighbor(x_i, alpha)
                f_j, _, _ = self.evaluate(x_j)

                if f_j > f_i:
                    x_i = x_j
                    f_i = f_j
                else:
                    pb = math.exp((f_j -f_i)/T)
                    if random.random() < pb:
                        x_i = x_j
                        f_i = f_j
            
            T     = beta*T
            alpha = alpha*beta
            self.log.write(f"k = {k}: x = {x_i} | f(x) = {f_i:.4f} | T = {T:.2f} | alpha = {alpha:.2f}\n")
            self.data_opt.append({"k": k, "score": f_i, "T": T, "alpha": alpha})
            
        self.log.flush()
        return x_i, f_i