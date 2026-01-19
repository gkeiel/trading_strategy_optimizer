import os, sys, traceback, itertools
from core.loader import Loader
from core.strategies import Strategies
from core.optimizer import Optimizer
from core.visualizer import Visualizer
from core.exporter import Exporter
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def run_tso(on_log=None):
        
    def log(msg):
        if on_log: on_log(msg)
        else: print(msg)
        
    # import configuration files
    loader       = Loader("config/config.json", "config/tickers.json")
    tickers      = loader.load_tickers()
    search_space = loader.load_search_space()
    
    # initialize cache dictionaries
    raw_data = {}
    pro_data = {}
    res_data = {}
    
    try:
        # download data and run optimization (for each ticker and indicator)
        for ticker, indicators_space in itertools.product(tickers, search_space):

            # download data (only once)
            if ticker not in raw_data:
                log(f"Downloading data for {ticker}.")
                raw_data[ticker] = loader.download_data(ticker)
            df = raw_data[ticker].copy()
            
            # run optimization
            log(f"Optimizing for {ticker}.")
            optimization = Optimizer(df, indicators_space)
            step_data    = optimization.search()
            
            if ticker not in res_data:
                res_data[ticker] = {}
                pro_data[ticker] = {}

            # visualize results
            for step in step_data:
                
                # store processed data and result data
                indicator, df, metrics = step["indicator"], step["df"], step["metrics"]
                ind_t  = indicator["ind_t"]  # indicator title
                ind_p  = indicator["ind_p"]  # indicator parameters
                params = "_".join(str(p) for p in ind_p)
                label  = f"{ticker}_{ind_t}_{params}"
                pro_data[ticker][label] = df.copy()
                res_data[ticker][label] = {
                    "Indicator": ind_t,
                    "Parameters": ind_p,
                    **metrics
                }
                
                visualizer = Visualizer(df)
                visualizer.plot_results(label)
            
            visualizer.plot_optimization(optimization.opt_global, optimization.opt_local, label)


        # compute best strategies (for each ticker)
        log("Consolidating results.")
        bst_data = Strategies().best_strategy(res_data)

        # export dataframe for analysis
        exporter = Exporter()
        exporter.export_dataframe(pro_data)
        
        # export backtesting results sorted by best
        exporter.export_best_results(bst_data)

        # update best strategies
        exporter.update_best_results(bst_data)
        
    except Exception as err:
        tb = traceback.format_exc()
        log(f"Error in main: {err}\n{tb}.")
        raise
    
def main():
    run_tso() 


if __name__ == "__main__":
    max_attempt = 3
    
    for attempt in range(1, max_attempt +1):
        try:
            print(f"Attempt {attempt} of {max_attempt}.")
            main()
            break
        
        except Exception as err:
            print(f"Error on attempt {attempt}: {err}.")
            if attempt == max_attempt:
                print("All attempts failed.")