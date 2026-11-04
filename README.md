# Week 5: Apparel & Textiles Trend Analysis and Forecasting

## Project overview
This project uses a public historical time series to study retail-sales trends and produce a transparent 12-month forecast. It demonstrates data acquisition, cleaning, exploratory analysis, feature engineering, baseline forecasting, model evaluation, visualization, and business interpretation.

**Research question:** What do historical monthly sales patterns suggest about near-term U.S. clothing and clothing-accessory retail sales, and how do simple forecasting models compare on unseen observations?

## Objectives
1. Obtain a credible, publicly accessible historical dataset.
2. Check dates, missing observations, duplicates, numeric values, frequency, and units.
3. Explore long-run trend and month-to-month/year-to-year movement.
4. Compare three forecasting methods using a chronological holdout rather than a random split.
5. Evaluate predictions with MAE, RMSE, and MAPE where meaningful.
6. Produce forecast scenarios and translate them into cautious operational recommendations.

## Dataset and source
- **Series:** Retail Sales: Clothing and Clothing Accessory Stores
- **Series ID:** `MRTSSM448USS`
- **Provider:** U.S. Census Bureau, distributed through FRED (Federal Reserve Bank of St. Louis)
- **Frequency:** Monthly
- **Units:** Millions of dollars, seasonally adjusted
- **Download:** [FRED series page](https://fred.stlouisfed.org/series/MRTSSM448USS)
- **CSV endpoint used by the script:** `https://fred.stlouisfed.org/graph/fredgraph.csv?id=MRTSSM448USS`

The series measures U.S. clothing and clothing-accessory store sales. It is not a direct measurement of textile production, individual garments sold, profit, consumer sentiment, or Indian apparel sales. Because it is denominated in dollars, movement can reflect prices as well as sales volume. FRED/Census observations may be revised after publication.

## Repository contents
```text
.
├── README.md
├── requirements.txt
├── .gitignore
└── src/
    └── analysis.py
```

- **`src/analysis.py`** downloads and validates the data, calculates trend indicators, evaluates the forecasting methods, writes result tables, and saves visualizations.
- **`requirements.txt`** lists the Python packages required to run the analysis.
- **`.gitignore`** excludes local environments, Python cache files, secrets, and generated `outputs/` artifacts from Git.
- **`outputs/`** is created when the script runs. Generated files are not committed by default, so the latest analysis can be reproduced from the source.

## Setup and execution
Recommended: Python 3.10 or newer and an internet connection to retrieve FRED data.

```bash
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\\Scripts\\Activate.ps1
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

Install dependencies and run:

```bash
python -m pip install -r requirements.txt
python src/analysis.py
```

The script prints the data coverage, number of observations, model metrics, and a preview of future forecasts. It creates the `outputs/` directory automatically.

## Data preparation and exploratory analysis
The script converts the date column to a datetime index and sales values to numeric values. Invalid dates and missing numeric values are removed, duplicate dates are reduced to one observation, and the series is sorted chronologically and assigned monthly-start frequency. A one-month gap may be interpolated; longer gaps remain missing and are dropped after interpolation. The script checks that enough history exists for seasonal forecasting.

The historical output adds:
- **Month-over-month change:** percentage change from the immediately preceding month.
- **Year-over-year change:** percentage change from the same month one year earlier.
- **12-month moving average:** a smoothed view of the broader trend.

The historical chart plots the monthly series and its 12-month moving average. Use it to distinguish broad direction from short-lived fluctuations. Sudden disruptions should be investigated rather than automatically interpreted as normal seasonality.

## Forecasting methods
### 1. Seasonal-naive baseline
For each future month, use the observed value from the corresponding month in the latest annual cycle. This provides a simple baseline that preserves a repeating annual pattern. It is easy to explain but cannot independently learn a changing trend.

### 2. 12-month moving average
Average the latest 12 observations to smooth short-term variation. For forecasts beyond one step, the script recursively includes prior predictions in the rolling window. This is transparent and useful as a baseline, but it tends to flatten turning points and can lag a changing market.

### 3. Holt–Winters exponential smoothing
The additive Holt–Winters model estimates a level, an additive trend, and a repeating 12-month seasonal component. Recent observations influence the estimated components according to fitted smoothing parameters. It can represent trend plus seasonality, but its assumptions may not hold after major structural changes.

These are statistical extrapolations from historical sales, not causal models. They do not directly account for inflation, product mix, weather, tariffs, consumer preferences, marketing campaigns, online-channel shifts, or supply-chain disruptions.

## Evaluation design
The most recent **12 months** are held out as a test set. The models are fitted using only earlier observations, then predict the held-out months. All methods are compared on the same test dates. This chronological split better reflects forecasting into the future than randomly mixing dates across train and test sets.

Metrics:
- **MAE (Mean Absolute Error):** average absolute difference between actual and forecast values. Units are millions of dollars; lower is better.
- **RMSE (Root Mean Squared Error):** square root of mean squared error. It penalizes large misses more strongly; lower is better.
- **MAPE (Mean Absolute Percentage Error):** mean absolute percentage error for non-zero actual values; lower is better, but percentage errors can be unstable when actual values are near zero.

The script sorts the comparison table by holdout RMSE and uses the lowest-RMSE method as a simple default for the forecast table. This is a decision rule for the exercise, not proof that the model will remain best in future periods. Review all metrics and the forecast chart before using the results.

## Output files
After a successful run, `outputs/` should contain:

| File | Purpose |
|---|---|
| `historical_sales.csv` | Original monthly sales plus MoM, YoY, and rolling-average indicators |
| `historical_trend.png` | Historical sales and 12-month average |
| `model_comparison.csv` | MAE, RMSE, and MAPE for each method on the holdout period |
| `holdout_forecasts.csv` | Actual holdout values and forecasts from each model |
| `holdout_comparison.png` | Visual comparison of holdout actuals and predictions |
| `12_month_forecasts.csv` | Forecast values from all methods and the holdout-RMSE selection |
| `12_month_forecasts.png` | Historical context and 12-month forecast scenarios |

These values and charts are generated when the script runs; no forecast score is asserted in advance. The script requires internet access to retrieve the latest available observations.

## Interpretation and business recommendations
Use the generated results to support, not replace, business judgment:

1. **Inventory planning:** consider the forecast range alongside current stock, stockout costs, supplier lead times, and minimum order quantities.
2. **Buying and assortment:** use persistent trend changes as a reason to investigate categories and channels with more granular data. This aggregate series cannot identify specific garments or sizes.
3. **Promotions and markdowns:** if demand uncertainty is high, test smaller replenishment batches and plan markdown contingencies rather than committing to one precise forecast.
4. **Budgeting and staffing:** use forecast scenarios for preliminary planning, then adjust for known campaigns, holidays, supplier constraints, and store-specific conditions.
5. **Monitoring:** refresh the model monthly, compare new actuals with forecasts, and investigate repeated forecast misses.
6. **Qualitative context:** combine the quantitative series with evidence about customer preferences, e-commerce, prices, weather, competitors, and input costs. Those factors are not included in this dataset.

### Risks and limitations
- The data is an aggregate U.S. retail-sales series, not textile-manufacturing data or a view of the Indian market.
- Nominal dollar values do not separate price effects from changes in quantity sold.
- Historical seasonality may change; unusual events can make previous patterns unreliable.
- Results depend on data revisions, the chosen holdout window, and model assumptions.
- A model with the lowest error in one test window may not win in another.
- The project does not establish causal explanations or guarantee future outcomes.

## Suggested report structure for the internship submission
1. Title and objective
2. Business problem and research question
3. Dataset description and source
4. Data cleaning and preparation
5. Exploratory trend analysis
6. Forecasting methods and assumptions
7. Train/test design and evaluation metrics
8. Results tables and chart interpretation (insert generated outputs)
9. Market impacts, risks, and opportunities
10. Recommendations, limitations, and conclusion
11. References

## Reference
U.S. Census Bureau. *Retail Sales: Clothing and Clothing Accessory Stores* (FRED series `MRTSSM448USS`). Federal Reserve Bank of St. Louis. https://fred.stlouisfed.org/series/MRTSSM448USS
