# Trading Strategy Optimizer

This project provides a Python script for **backtesting and heuristic optimization of trading strategies based on technical indicators**, being applied to spot market time series.

As main advantages, the project provides:
- **simulated annealing algorithm** to perform a global search for the best strategies. 
- creation of **spreadsheets and figures with performance results** from backtesting and optimization procedure.
- **open-source code**, allowing **flexibility in adjusting the search space** and **implementing technical indicators**.


## 🗂 Project Structure

The project is organized around a modular pipeline, where each class has a responsibility:

- **Loader** handles configuration files for tickers and market settings.
- **Indicator** applies technical indicators (MA crossover, Bollinger Bands, MACD) and generates trading signals.
- **Backtester** evaluates strategies on historical data and computes performance metrics.
- **Optimizer** searches the indicator parameter space using heuristic optimization.
- **Strategies** scores and ranks candidate strategies based on configurable objective functions.


The project has the following structure:

 ```text
 trading_strategy_optimizer/ 
 │  
 ├── trading_strategy_optimizer.py 
 |  
 ├── core/   
 │   ├── __init__.py  
 │   ├── loader.py  
 │   ├── indicator.py  
 │   ├── backtester.py  
 │   ├── optimizer.py  
 │   ├── strategies.py  
 │   ├── exporter.py  
 │   └── notifier.py  
 │  
 ├── config/  
 │   ├── config.json  
 │   └── tickers.json  
 │  
 ├── data/  
 │   └── results/ 
 |       ├── best_results.xlsx 
 │       ├── strategies.csv  
 │       ├── backtests.png   
 │       └── logs.txt   
 │  
 ├── requirements.txt  
 ├── README.md  
 └── LICENSE  
 ```

## 📈 Available Strategies

The project currently supports the following indicators:
- **Moving Average crossover** using:
  - **SMA (Simple Moving Average)**;
  - **EMA (Exponential Moving Average)**;
  - **WMA (Weighted Moving Average)**.
- **Bollinger bands**;
- **Moving Average Convergence/Divergence (MACD)**.

## ⚙️ How to Use

1. **Install dependencies**:
   ```bash
    pip install pandas
    pip install numpy
    pip install yfinance
    pip install requests
    ```

2. **Configure tickers and indicators**
   - In `config/config.json` add the configuration parameters.
   - In `config/tickers.json` add the stock symbols to analyze, one per line.

3. **Run the script**
   - To run the optimization with backtests, execute:
     ```bash
     python trading_strategy_optimizer.py
     ```

## 🧩 Output Examples

- **Backtest charts for MACD strategy**
  
  After running `trading_strategy_optimizer.py` optimization it is generated strategy charts, spreadsheets for each ticker, and a summary with best results. The generated figures follow the example:

  <p align="center">
     <img width="733" height="395" alt="TSLA_MACD_20_28_9" src="https://github.com/user-attachments/assets/97f0faf7-ec23-4bcd-aa4b-60958afa29df" />
     <img width="733" height="395" alt="TSLA_MACD_20_28_9_backtest" src="https://github.com/user-attachments/assets/cedf4732-580d-4055-8d2a-da8be74cb316" />
  </p>

  Notice that the asset ends the evaluated periodo at 1.75 times its initial price, so a Buy & hold strategy would yield 175% return. On the other hand, strictly following the MACD 20/28/9 strategy would produce above 400% return over the same period, excluding any trasactions fees.

- **Optimization log and charts for MACD strategy**

  After running `trading_strategy_optimizer.py` it is generated optimization logs and charts, for each ticker, are. The generated files follow the example:

  ```txt
  k = 1: x = {'ind_t': 'MACD', 'ind_p': [15, 33, 8]} | f(x) = 3.4567 | T = 0.95 | alpha = 0.95
  k = 2: x = {'ind_t': 'MACD', 'ind_p': [16, 35, 8]} | f(x) = 2.9417 | T = 0.90 | alpha = 0.90
  k = 3: x = {'ind_t': 'MACD', 'ind_p': [16, 35, 8]} | f(x) = 2.9417 | T = 0.86 | alpha = 0.86
  k = 4: x = {'ind_t': 'MACD', 'ind_p': [16, 35, 8]} | f(x) = 2.9417 | T = 0.81 | alpha = 0.81
  k = 5: x = {'ind_t': 'MACD', 'ind_p': [15, 29, 10]} | f(x) = 2.7759 | T = 0.77 | alpha = 0.77
  k = 6: x = {'ind_t': 'MACD', 'ind_p': [14, 29, 11]} | f(x) = 3.1750 | T = 0.74 | alpha = 0.74
  k = 7: x = {'ind_t': 'MACD', 'ind_p': [14, 25, 12]} | f(x) = 3.6865 | T = 0.70 | alpha = 0.70
  k = 8: x = {'ind_t': 'MACD', 'ind_p': [15, 23, 11]} | f(x) = 3.1755 | T = 0.66 | alpha = 0.66
  k = 9: x = {'ind_t': 'MACD', 'ind_p': [17, 26, 9]} | f(x) = 3.3936 | T = 0.63 | alpha = 0.63
  k = 10: x = {'ind_t': 'MACD', 'ind_p': [19, 21, 8]} | f(x) = 2.7423 | T = 0.60 | alpha = 0.60
  k = 11: x = {'ind_t': 'MACD', 'ind_p': [19, 26, 8]} | f(x) = 3.7286 | T = 0.57 | alpha = 0.57
  k = 12: x = {'ind_t': 'MACD', 'ind_p': [20, 23, 9]} | f(x) = 3.2371 | T = 0.54 | alpha = 0.54
  k = 13: x = {'ind_t': 'MACD', 'ind_p': [20, 23, 9]} | f(x) = 3.2371 | T = 0.51 | alpha = 0.51
  k = 14: x = {'ind_t': 'MACD', 'ind_p': [20, 25, 9]} | f(x) = 3.1177 | T = 0.49 | alpha = 0.49
  k = 15: x = {'ind_t': 'MACD', 'ind_p': [19, 28, 9]} | f(x) = 3.6547 | T = 0.46 | alpha = 0.46
  k = 16: x = {'ind_t': 'MACD', 'ind_p': [19, 29, 8]} | f(x) = 3.0254 | T = 0.44 | alpha = 0.44
  k = 17: x = {'ind_t': 'MACD', 'ind_p': [20, 28, 8]} | f(x) = 3.0254 | T = 0.42 | alpha = 0.42
  k = 18: x = {'ind_t': 'MACD', 'ind_p': [19, 28, 7]} | f(x) = 3.3218 | T = 0.40 | alpha = 0.40
  k = 19: x = {'ind_t': 'MACD', 'ind_p': [19, 28, 7]} | f(x) = 3.3218 | T = 0.38 | alpha = 0.38
  k = 20: x = {'ind_t': 'MACD', 'ind_p': [19, 28, 7]} | f(x) = 3.3218 | T = 0.36 | alpha = 0.36
  k = 21: x = {'ind_t': 'MACD', 'ind_p': [19, 28, 7]} | f(x) = 3.3218 | T = 0.34 | alpha = 0.34
  k = 22: x = {'ind_t': 'MACD', 'ind_p': [19, 28, 7]} | f(x) = 3.3218 | T = 0.32 | alpha = 0.32
  k = 23: x = {'ind_t': 'MACD', 'ind_p': [18, 30, 8]} | f(x) = 2.9101 | T = 0.31 | alpha = 0.31
  k = 24: x = {'ind_t': 'MACD', 'ind_p': [20, 31, 7]} | f(x) = 2.8629 | T = 0.29 | alpha = 0.29
  k = 25: x = {'ind_t': 'MACD', 'ind_p': [20, 30, 7]} | f(x) = 2.8629 | T = 0.28 | alpha = 0.28
  k = 26: x = {'ind_t': 'MACD', 'ind_p': [19, 33, 7]} | f(x) = 2.8629 | T = 0.26 | alpha = 0.26
  k = 27: x = {'ind_t': 'MACD', 'ind_p': [18, 33, 8]} | f(x) = 2.9565 | T = 0.25 | alpha = 0.25
  k = 28: x = {'ind_t': 'MACD', 'ind_p': [18, 33, 8]} | f(x) = 2.9565 | T = 0.24 | alpha = 0.24
  k = 29: x = {'ind_t': 'MACD', 'ind_p': [18, 31, 9]} | f(x) = 3.4574 | T = 0.23 | alpha = 0.23
  k = 30: x = {'ind_t': 'MACD', 'ind_p': [18, 28, 8]} | f(x) = 3.5259 | T = 0.21 | alpha = 0.21
  k = 31: x = {'ind_t': 'MACD', 'ind_p': [18, 28, 8]} | f(x) = 3.5259 | T = 0.20 | alpha = 0.20
  k = 32: x = {'ind_t': 'MACD', 'ind_p': [18, 28, 8]} | f(x) = 3.5259 | T = 0.19 | alpha = 0.19
  k = 33: x = {'ind_t': 'MACD', 'ind_p': [18, 28, 8]} | f(x) = 3.5259 | T = 0.18 | alpha = 0.18
  k = 34: x = {'ind_t': 'MACD', 'ind_p': [18, 28, 8]} | f(x) = 3.5259 | T = 0.17 | alpha = 0.17
  k = 35: x = {'ind_t': 'MACD', 'ind_p': [18, 28, 8]} | f(x) = 3.5259 | T = 0.17 | alpha = 0.17
  k = 36: x = {'ind_t': 'MACD', 'ind_p': [19, 29, 9]} | f(x) = 3.4574 | T = 0.16 | alpha = 0.16
  k = 37: x = {'ind_t': 'MACD', 'ind_p': [19, 29, 9]} | f(x) = 3.4574 | T = 0.15 | alpha = 0.15
  k = 38: x = {'ind_t': 'MACD', 'ind_p': [19, 29, 9]} | f(x) = 3.4574 | T = 0.14 | alpha = 0.14
  k = 39: x = {'ind_t': 'MACD', 'ind_p': [19, 29, 9]} | f(x) = 3.4574 | T = 0.14 | alpha = 0.14
  k = 40: x = {'ind_t': 'MACD', 'ind_p': [19, 29, 9]} | f(x) = 3.4574 | T = 0.13 | alpha = 0.13
  k = 41: x = {'ind_t': 'MACD', 'ind_p': [18, 28, 8]} | f(x) = 3.5259 | T = 0.12 | alpha = 0.12
  k = 42: x = {'ind_t': 'MACD', 'ind_p': [19, 27, 9]} | f(x) = 3.5202 | T = 0.12 | alpha = 0.12
  k = 43: x = {'ind_t': 'MACD', 'ind_p': [20, 28, 9]} | f(x) = 3.6568 | T = 0.11 | alpha = 0.11
  k = 44: x = {'ind_t': 'MACD', 'ind_p': [20, 28, 9]} | f(x) = 3.6568 | T = 0.10 | alpha = 0.10
  k = 45: x = {'ind_t': 'MACD', 'ind_p': [20, 28, 9]} | f(x) = 3.6568 | T = 0.10 | alpha = 0.10
  ```
  <p align="center">
     <img width="733" height="395" alt="TSLA_MACD_optimization" src="https://github.com/user-attachments/assets/0a9b1f9d-7f2e-4710-8eee-bb9ae141f796" />
  </p>
  
  
## 📌 Notes

⚠️ We are not responsible for any financial losses resulting from the use of the strategies or signals generated by this code.

- Contributions are welcome! Open an issue or submit a pull request.
- Future improvements and new features may be added, including:
  - migration to object-oriented programming (OOP); ✅
  - improve objective function with new weights and presets; ✅
  - improve optimization techniques;
  - file saving in cloud.

## 🤝 Support

This repository is independently maintained, only in free time. If you find the code useful and wish to support its continued development, consider donating:

- [PayPal](https://www.paypal.com/donate/?hosted_button_id=BF6E8J7P32KWE)  

Your support helps keep the project alive and evolving, by adding new optimization methods, improvements and documentation.
