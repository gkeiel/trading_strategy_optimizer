from .indicator import Indicator
from .backtester import Backtester
from .strategies import Strategies
import json, math, random, copy, itertools


# =====================================================
#  Optimizer
# =====================================================
class Optimizer:
    def __init__(self, df, search_space, file_config="config/config.json"):
        self.df         = df
        self.space      = search_space
        self.data       = []
        self.opt_local  = []
        self.opt_global = []
        self.cache      = {}
        self.load_config(file_config)
        
    def load_config(self, path):
        with open(path, "r", encoding="utf-8") as f: config = json.load(f)
        self.sa_cfg = config.get("simulated_annealing", {})
        self.hc_cfg = config.get("hill_climbing", {})
        self.gs_cfg = config.get("grid_search", {})
        
    def evaluate(self, indicator):
        indicator_key = (indicator["ind_t"], tuple(indicator["ind_p"]))

        if indicator_key in self.cache:
            return self.cache[indicator_key]
        
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
            "Trades": df["Cumulative_Trades"].iloc[-1],
            "Sharpe": df["Strategy"].mean() / df["Strategy"].std()*pow(len(df), 0.5),
            "Max_Drawdown": abs(df["Drawdown"].min()),
        }
        
        # compute score
        score = Strategies().compute_score(metrics)
        
        # append to data
        self.cache[indicator_key] = (score, df, metrics)
        self.data.append({"indicator": indicator, "df": df, "metrics": metrics, "score": score})
        return score, df, metrics
    
    def search(self):
        start_indicator = {"ind_t": self.space["ind_t"], "ind_p": [p["min"] for p in self.space["params"]]}
        self.log   = open(f"data/results/{start_indicator['ind_t']}_log.txt", "w")
        
        if self.sa_cfg.get("enabled"):  
            best_params, best_score = self.simulated_annealing(start_indicator=start_indicator)
        if self.hc_cfg.get("enabled"):
            best_params, best_score = self.hill_climbing(start_indicator=start_indicator)
        if self.gs_cfg.get("enabled"):
            best_params, best_score = self.grid_search(start_indicator=start_indicator)
        self.log.close()
        return self.data
    
    def random_neighbor(self, indicator, alpha):
        x = copy.deepcopy(indicator)

        for i, val in enumerate(x["ind_p"]):
            pmin  = self.space["params"][i]["min"]
            pmax  = self.space["params"][i]["max"]
            step  = max(1, round(alpha*(pmax -pmin)/4))
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

    def hill_climbing(self, start_indicator, alpha=1, eps=1e-6, k_limit=5):
        n            = self.hc_cfg.get("n", 3)
        k_max        = self.hc_cfg.get("k_max", 50)
        x_i          = start_indicator
        f_i, _, _    = self.evaluate(x_i)
        k            = 0
        k_no_improve = 0
                
        while k < k_max:
            k = k +1
            
            for _ in range(n):
                x_j       = self.random_neighbor(x_i, alpha)
                f_j, _, _ = self.evaluate(x_j)
                self.opt_local.append({"k": k, "score": f_i, "alpha": alpha, "params": x_j["ind_p"].copy()})
                
                if f_j > f_i +eps:
                    x_i = x_j
                    f_i = f_j
                    flag_improve = True
                    
            self.opt_global.append({"k": k, "score": f_i, "T": None, "alpha": alpha, "params": x_i["ind_p"].copy()})
            self.log.write(f"k = {k}: x = {x_i} | f(x) = {f_i:.4f} | alpha = {alpha:.2f}\n")
            if flag_improve: k_no_improve = 0
            else: k_no_improve += 1
            if k_no_improve >= k_limit: break

        return x_i, f_i
    
    def simulated_annealing(self, start_indicator, alpha=1, beta_alpha=0.9, beta=0.95, eps=1e-6, k_limit=5):
        n            = self.sa_cfg.get("n", 3)
        k_max        = self.sa_cfg.get("k_max", 50)
        x_i          = start_indicator
        f_i, _, _    = self.evaluate(x_i)
        T            = 1
        k            = 0
        k_no_improve = 0
        
        while k < k_max:
            k = k +1
            
            for _ in range(n):
                x_j       = self.random_neighbor(x_i, alpha)
                f_j, _, _ = self.evaluate(x_j)
                self.opt_local.append({"k": k, "score": f_j, "T": T, "alpha": alpha, "params": x_j["ind_p"].copy()})

                if f_j > f_i +eps:
                    x_i = x_j
                    f_i = f_j
                    k_no_improve = 0
                else:
                    pb = math.exp((f_j -f_i)/T)
                    if random.random() < pb:
                        x_i = x_j
                        f_i = f_j
                        k_no_improve = 0
                    else: k_no_improve += 1
                        
            T     = beta*T
            alpha = beta_alpha*alpha
            self.opt_global.append({"k": k, "score": f_i, "T": T, "alpha": alpha, "params": x_i["ind_p"].copy()})
            self.log.write(f"k = {k}: x = {x_i} | f(x) = {f_i:.4f} | T = {T:.2f} | alpha = {alpha:.2f}\n")
            if k_no_improve >= k_limit: break
            
        self.log.flush()
        return x_i, f_i
    
    def grid_search(self, start_indicator):
        alpha = self.gs_cfg.get("alpha", 5)
        grid  = [range(p["min"], p["max"]+1, alpha) for p in self.space["params"]]        
        x_i   = start_indicator
        k     = 0
        
        for params in itertools.product(*grid):
            k = k+1       
            x_i       = {"ind_t": start_indicator["ind_t"], "ind_p": list(params)}           
            f_i, _, _ = self.evaluate(x_i)
            self.opt_local.append({"k": k, "score": f_i, "T": None, "alpha": None, "params": x_i["ind_p"].copy()})
            self.log.write(f"k = {k}: x = {x_i} | f(x) = {f_i:.4f}\n")
            
        self.opt_global = self.opt_local
        return x_i, f_i