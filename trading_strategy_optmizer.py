import os, sys, traceback
from core.loader import Loader
from core.strategies import Strategies
from core.optimizer import Optimizer
from core.exporter import Exporter
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    # import configuration files
    loader       = Loader("config/config.json", "config/tickers.json")
    tickers      = loader.load_tickers()
    search_space = loader.load_search_space()
    
    # initialize cache dictionaries
    raw_data = {}
    pro_data = {}
    res_data = {}

    try:
        # download data and run optimization (for each ticker)
        for ticker in tickers:

            # download data (only once)
            if ticker not in raw_data:
                raw_data[ticker] = loader.download_data(ticker)
            df = raw_data[ticker]
            
            # run optimization
            step_data = Optimizer(df, search_space).search()
            
            if ticker not in res_data:
                res_data[ticker] = {}
                pro_data[ticker] = {}

            for step in step_data:
                indicator = step["indicator"]
                df        = step["df"]
                metrics   = step["metrics"]
                
                # store processed data and result data
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

        # compute best strategies (for each ticker)
        bst_data = Strategies().best_strategy(res_data)

        # exports dataframe for analysis
        exporter = Exporter()
        exporter.export_dataframe(pro_data)
        
        # exports backtesting results
        exporter.export_results(res_data)

        # exports backtesting results sorted by best
        exporter.export_best_results(bst_data)

        # updates best strategies
        exporter.update_best_results(bst_data)
        
    except Exception as err:
        tb = traceback.format_exc()
        print(f"Fatal error in main: {err}\n{tb}.")
        sys.exit(1)


if __name__ == "__main__":
    max_attempt = 3
    
    for attempt in range(1, max_attempt+1):
        try:
            print(f"Attempt {attempt} of {max_attempt}.")
            main()
            break
        except Exception as err:
            print(f"Error on attempt {attempt}: {err}.")
            if attempt == max_attempt:
                print("All attempts failed.")