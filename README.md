# Trading Strategy Optimizer

This project provides a Python script for **backtesting and optimizing trading strategies based on technical indicators**, being applied to spot market time series. Additionally, it includes a script for **automatic generation of buy and sell signals for global assets** for the optimized strategy.

As main advantages, the project provides:
- **simulated annealing algorithm** to perform a global search for the best strategies. 
- recurring **trading signals and information via Telegram channel** to **avoid the need for manual chart analysis**.
- **open-source code**, allowing **flexibility in choosing technical indicators** and comparing all strategies.

Telegram open channel with daily signals run via GitHub Actions. Anyone can sign up to get a feel for what the bot can offer.
[t.me/market_trading_signals_free](https://t.me/market_trading_signals_free)


## 🗂 Project Structure

The project is organized around a modular pipeline, where each class has a responsibility:

- **Loader** handles configuration files for tickers and market settings.
- **Indicator** applies technical indicators (MA crossover, Bollinger Bands, MACD) and generates trading signals.
- **Backtester** evaluates strategies on historical data and computes performance metrics.
- **Optimizer** searches the indicator parameter space using heuristic optimization.
- **Strategies** scores and ranks candidate strategies based on configurable objective functions.
- **Notifier** generate recurrent signals and notifications for a Telegram bot.



The project has the following structure:

 ```text
 trading_strategy_optimizer/ 
 │  
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
 ├── trading_strategy_optimizer.py  
 ├── trading_strategy_bot.py  
 │  
 ├── .github/  
 │   └── workflows/  
 │       └── trading_strategy_bot.yml  
 │  
 ├── requirements.txt  
 ├── README.md  
 └── LICENSE  
 ```

## 📈 Available Strategies

The project currently supports the following indicators:
- **Moving average crossover** using:
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
    pip install python-dotenv
    ```

2. **Configure tickers and indicators**
   - In `config.json` add the various configuration parameters.
   - In `tickers.json` add the stock codes to analyze, one per line.
   - In `strategies.csv` lists the stocks to generate trading signals, each with its corresponding best strategy.

3. **Configure Telegram**
   - Create a Telegram bot and obtain its `TOKEN`.
   - Create a Telegram channel and obtain its `CHAT_ID`.
   - Add the bot as channel administrator.

4. **Run the script**
   - To run the optimization with backtests, execute:
     ```bash
     python trading_strategy_optimizer.py
     ```
   - To generate recurrent trading signals and notifications for each ticker, execute:
     ```bash
     python trading_strategy_bot.py
     ```
   - To automate the signal generation with GitHub Actions, create the repository secrets `TOKEN` and `CHAT_ID` for the preconfigured workflow.

## 🖼️ Output Examples

- **Backtest chart with SMA crossover**
  
  After running `trading_strategy_optimizer.py` optimization it generates strategy charts, spreadsheets for each ticker, and a summary with best results. The generated figures follow the example below:

  <p align="center">
     <img width="733" height="395" alt="TSLA_SMA_20_30" src="https://github.com/user-attachments/assets/cf810a16-0d6e-4f8d-89ad-51303f7a24b8" />
     <img width="733" height="395" alt="TSLA_SMA_20_30_backtest" src="https://github.com/user-attachments/assets/8a3ace24-e11c-42fb-a812-37a192b757bc" />
  </p>
  
  Notice that the asset ends the evaluated periodo at 1.75 times its initial price, so a Buy & hold strategy would yield 175% return. On the other hand, strictly following the SMA 20/30 strategy would produce above 250% return over the same period, excluding any trasactions fees. Furthermore, short selling operations are ignored by default in calculations assuming there exist borrowing fees involved, though they can easily be enabled in the backtest.

- **Trading signals via Telegram**

  After running `trading_strategy_bot.py`, it generates trading signals for the selected (best) strategies, as the example below:
  <p align="center">
     <img width="480" height="511" alt="telegram" src="https://github.com/user-attachments/assets/39ac0ee0-c816-4bd6-8742-b4884156051a" />
  </p>

  Notice that a trading signal is generated for each asset, suggesting an up, down or neutral tendency based on the selected strategy and this trend duration, showing how many samples its side remained unchanged. Additionaly, volume and confirmation moving average crossover data are displayed as strenght indicators for such trends.
  
## 🧩 Project Structure

- `trading_strategy_optimizer.py` → Main file for backtesting and search for the best strategies.
- `trading_strategy_bot.py` → Main file for generating recurrent trading signals and Telegram notifications.
- `tickers.json` → List of tickers to analyze.
- `indicators.json` → List of indicators to test.
- `strategies.csv` → List of selected strategies for trading signals, including tickers and their indicators.

## 📌 Notes

⚠️ We are not responsible for any financial losses resulting from the use of the strategies or signals generated by this code.

- Contributions are welcome! Open an issue or submit a pull request.
- Future improvements and new features may be added, including:
  - migration to object-oriented programming (OOP); ✅
  - improve objective function with new weights and presets; ✅
  - improve optimization techniques;
  - file saving in cloud;
  - e-mail alerts/reports.

## 🤝 Support

This repository is independently maintained, only in free time. If you find the code useful and wish to support its continued development, consider donating:

- [PayPal](https://www.paypal.com/donate/?hosted_button_id=BF6E8J7P32KWE)  

Your support helps keep the project alive and evolving, by adding new indicators, improvements, and documentation.
