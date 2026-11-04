# Week 5 Internship Report
## Apparel & Textiles Trend Analysis and Forecasting

**Project type:** Exploratory data analysis and time-series forecasting  
**Data source:** U.S. Census Bureau retail sales series distributed by FRED  
**Series:** MRTSSM448USS — Retail Sales: Clothing and Clothing Accessory Stores

> **Important:** Run `python src/analysis.py` before submitting a final results-based report. Insert the values and charts generated under `outputs/` into the Results section. This report intentionally does not fabricate model scores or future forecast values.

## 1. Executive summary
This project examines historical monthly U.S. clothing and clothing-accessory retail sales and compares three forecasting approaches: seasonal-naive, a 12-month moving average, and additive Holt–Winters exponential smoothing. The workflow combines time-series visualization, derived growth indicators, chronological holdout evaluation, and business interpretation. Its purpose is to demonstrate a reproducible forecasting process and explain how forecast evidence can inform inventory, buying, promotions, and risk planning.

The data represents aggregate nominal retail sales in millions of dollars. It should not be interpreted as apparel units sold, textile manufacturing output, profit, or Indian market activity. The final conclusions must be based on the generated outputs and read alongside these limitations.

## 2. Business problem
Apparel and textile businesses make decisions about purchasing, stock levels, staffing, promotions, and cash flow under uncertain demand. Ordering too much can increase storage costs and markdowns; ordering too little can cause stockouts and lost sales. Historical data can reveal broad trends and recurring patterns, but no model can guarantee future outcomes.

**Research question:** What do historical monthly U.S. clothing and clothing-accessory retail sales suggest about near-term sales, and which of three transparent forecasting methods performs best over a recent 12-month test period?

## 3. Objectives
1. Acquire a public historical monthly retail-sales series.
2. Clean and validate dates and numeric observations.
3. Explore the historical trend and calculate month-over-month and year-over-year changes.
4. Compare simple baseline and seasonal forecasting methods.
5. Evaluate predictions on unseen observations using MAE, RMSE, and MAPE.
6. Produce 12-month forecast scenarios and visualizations.
7. Discuss possible market impacts, risks, opportunities, and strategic uses.

## 4. Dataset description
The project uses FRED series **MRTSSM448USS**, sourced from the U.S. Census Bureau's Monthly Retail Trade and Food Services release.

- Frequency: monthly
- Units: millions of dollars
- Adjustment: seasonally adjusted
- Coverage: the date range available from the source at the time the script runs
- Access: https://fred.stlouisfed.org/series/MRTSSM448USS

The Python script downloads the current CSV version at runtime. Therefore, the latest date and number of observations should be taken from the console output and `outputs/historical_sales.csv`, not hard-coded into the report. The provider may revise historical observations.

## 5. Data preparation
The script performs these preparation steps:
1. Reads the CSV directly from FRED.
2. Parses the date field into a datetime index and converts sales to numeric values.
3. Removes invalid dates and missing numeric values.
4. Sorts observations by date and resolves duplicate dates.
5. assigns a monthly-start frequency and interpolates a gap only when it is one month long.
6. Checks that sufficient monthly history is available for annual seasonality.
7. Saves the prepared data with derived indicators to `outputs/historical_sales.csv`.

**Quality note:** Interpolation is a pragmatic handling choice, not a substitute for investigating missing source data. For a production analysis, document every missing period and consider sensitivity checks with and without imputed values.

## 6. Exploratory data analysis
The analysis calculates:
- **Month-over-month percentage change:** current month compared with the immediately preceding month.
- **Year-over-year percentage change:** current month compared with the same month a year earlier.
- **12-month moving average:** a smoothed series that reduces the influence of short-term movement.

The chart `outputs/historical_trend.png` overlays observed sales with the 12-month average. When interpreting it, describe the direction over the full period, identify major rises or drops, and distinguish persistent changes from brief fluctuations. Avoid attributing a change to a particular event unless independent evidence supports that explanation.

## 7. Forecasting methodology
### 7.1 Seasonal-naive forecast
Each future month is assigned the value observed in the same month of the most recent annual cycle. This method is easy to explain and provides a seasonal baseline. It assumes the seasonal pattern repeats and does not explicitly estimate a changing trend.

### 7.2 Twelve-month moving average
The forecast begins with the mean of the latest 12 observations. For subsequent months, prior predictions are added to the rolling history. This reduces short-term noise but can respond slowly to a real change in the underlying level or trend.

### 7.3 Additive Holt–Winters exponential smoothing
Holt–Winters estimates a level, additive trend, and additive seasonal pattern with a 12-month cycle. Model parameters are fitted from the training period. The method can represent trend and recurring seasonality but may perform poorly when the market undergoes a structural break or seasonal behavior changes.

## 8. Evaluation design and metrics
The latest 12 observations form the test set; all earlier observations form the training set. Each model is fitted or calculated using the training period only and predicts the same held-out months. This chronological evaluation better resembles a real forecasting task than randomly splitting time-series observations.

- **MAE:** mean absolute error; interpretable in millions of dollars.
- **RMSE:** square root of mean squared error; gives larger errors more influence.
- **MAPE:** mean absolute percentage error; useful as a relative measure but unstable around zero. The implementation excludes zero or near-zero actual values from its MAPE calculation.

Lower values generally indicate smaller errors for a given metric. Compare all metrics, inspect the actual-versus-predicted chart, and consider whether forecast behavior is plausible. The model with the lowest holdout RMSE is marked as the script's default selection, but one holdout period does not prove it will be best in the future.

## 9. Results — complete after running the code
Run:
```bash
python -m pip install -r requirements.txt
python src/analysis.py
```

Then insert the values from `outputs/model_comparison.csv`:

| Model | MAE | RMSE | MAPE (%) |
|---|---:|---:|---:|
| Seasonal-naive | Insert generated value | Insert generated value | Insert generated value |
| 12-month moving average | Insert generated value | Insert generated value | Insert generated value |
| Holt–Winters | Insert generated value | Insert generated value | Insert generated value |

Use `outputs/holdout_comparison.png` to describe where the methods over- or under-predict. Use `outputs/12_month_forecasts.csv` and `outputs/12_month_forecasts.png` to summarize the next 12 monthly forecast scenarios. Do not state that one model is more accurate until the generated metrics have been inspected.

### Visualizations to include
1. **Historical trend:** insert `historical_trend.png`; describe long-run direction, volatility, and the smoothed trend.
2. **Holdout evaluation:** insert `holdout_comparison.png`; compare actual sales against each model's predictions and discuss visible forecast misses.
3. **Future scenarios:** insert `12_month_forecasts.png`; compare the shape and spread of the forecasts and explain why disagreement among models is a sign of uncertainty.

## 10. Market implications
A forecast of aggregate retail sales can provide context for planning but is not enough to make product-level decisions. Retail sales may change because of prices, quantity sold, channel mix, consumer income, promotions, or the composition of stores in the data. The time series itself does not isolate these drivers.

Potential opportunities include improving the timing of replenishment, aligning promotional calendars with observed patterns, and preparing alternative budgets for stronger or weaker sales scenarios. Potential risks include over-ordering after a temporary rise, missing demand after an abrupt change, and assuming historical seasonal patterns will repeat unchanged.

## 11. Strategic recommendations
1. **Use scenarios rather than a single point estimate.** Compare all three forecasts and build conservative, base, and optimistic planning cases.
2. **Tie purchasing to operational constraints.** Check supplier lead times, minimum order quantities, current inventory, storage costs, and cash availability before acting.
3. **Monitor forecast errors monthly.** Once new observations arrive, compare them with the previous forecasts and investigate repeated misses.
4. **Avoid overreacting to one observation.** Confirm whether a change persists and look for corroborating evidence before making large inventory decisions.
5. **Add more relevant data where possible.** For company-level decisions, include product/category sales, prices, promotions, stockouts, online/offline channels, regional demand, and inventory.
6. **Document assumptions.** Record the data download date, forecast horizon, model version, evaluation window, and any changes to the source data.

## 12. Limitations and future work
- The source is aggregate U.S. clothing and clothing-accessory store sales, not Indian market or textile factory data.
- Sales are in nominal dollars and do not isolate inflation or units sold.
- The model uses only the target series and has no external explanatory variables.
- Historical patterns may shift after economic, consumer, or supply-chain shocks.
- Results depend on data revisions and the selected 12-month holdout.
- Future work could test rolling-origin backtesting, prediction intervals, multiplicative seasonality, ARIMA/SARIMA, inflation-adjusted sales, and additional public indicators. Any added model should be compared on the same evaluation design.

## 13. Conclusion
This project establishes a reproducible pipeline from public data acquisition to trend visualization, forecast evaluation, and business recommendations. The most useful model should be chosen only after inspecting generated error metrics and forecast behavior. Forecasts should support inventory and commercial decisions alongside more granular operational data and qualitative market intelligence, not be treated as certain outcomes.

## References
1. U.S. Census Bureau, *Retail Sales: Clothing and Clothing Accessory Stores*, FRED series MRTSSM448USS, Federal Reserve Bank of St. Louis: https://fred.stlouisfed.org/series/MRTSSM448USS
2. FRED data table: https://fred.stlouisfed.org/data/MRTSSM448USS
