from .indicator import Indicator
from .backtester import Backtester
from .strategies import Strategies
import math, random, copy


# =====================================================
#  Optimizer
# =====================================================
class Optimizer:
    def __init__(self, df, search_space):
        self.df    = df
        self.space = search_space
        self.data  = []

    def evaluate(self, params):
        df = self.df.copy()
        
        # setup indicator
        df = Indicator(params).setup_indicator(df)

        # run backtest
        backtest = Backtester(df)
        df       = backtest.run_strategy(params)
                
        # compute metrics
        metrics = {
            "Return_Market": df["Cumulative_Market"].iloc[-1],
            "Return_Strategy": df["Cumulative_Strategy"].iloc[-1],
            "Trades": df["Cumulative_Trades"].iloc[-1]//2,
            "Sharpe": df["Strategy"].mean() / df["Strategy"].std()*pow(len(df), 0.5),
            "Max_Drawdown": abs(df["Drawdown"].min()),
        }
        # backtest.plot_res("TEST")
        
        # compute score
        score = Strategies().compute_score(metrics)
        
        # append
        self.data.append({"indicator": params, "df": df, "metrics": metrics, "score": score})
        return score, df, metrics
    
    def search(self):
        start_params = {
            "ind_t": self.space["ind_t"],
            "ind_p": [
                int((p["min"] +p["max"])/2)
                for p in self.space["params"]
            ]
        }
        
        best_params, best_score = self.simulated_annealing(start_params=start_params)
        return self.data
    
    def random_neighbor(self, params, alpha):
        x = copy.deepcopy(params)

        for i, val in enumerate(x["ind_p"]):
            pmin  = self.space["params"][i]["min"]
            pmax  = self.space["params"][i]["max"]
            new_v = val +random.randint(-alpha, alpha)
            x["ind_p"][i] = max(pmin, min(pmax, new_v))
        return x

    def hill_climbing(self, start_params, alpha=5, n=5, k_max=30):
        x_i       = start_params
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
    
    def simulated_annealing(self, start_params, alpha=10, beta=0.98, T_0=1, n=5, k_max=30):
        x_i       = start_params
        f_i, _, _ = self.evaluate(x_i)
        T         = T_0
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
            alpha = max(1, int(alpha*beta))

        return x_i, f_i