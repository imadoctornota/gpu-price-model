# When will GPU prices go down?

Code and results for my video on whether anything predicts GPU prices, and whether waiting to buy a graphics card actually pays off. Video: (link goes here once it's up)

I'm a doctor, not a quant. This is one notebook that rebuilds ten years of GPU prices from free data, tests a bunch of predictors without letting them see the future, and simulates buying a card now vs waiting.

## What I found (data through October 2026)

- GPU performance got about 51% more expensive in a year. That's dollars per 1,000 PassMark G3D Mark points, using the three best-value cards launched in the last three years. The same three cards that were the best deals in October 2025 (RTX 5060, RTX 5050, RX 7600) rose 52%.
- It wasn't every card. The cheapest way to get GTX 1060-level performance stayed at about $195. The cheapest RTX 3060-level card rose 31% and the cheapest RTX 4070-level card rose 50%.
- Nothing I tried beat "prices stay where they are" in a way that survives correcting for the number of tests. That includes memory-maker stocks, NVIDIA and AMD stock, the S&P 500, launch timing, the calendar and the price trend itself.
- The one predictor that stood out was Bitcoin's 3-month change: +13.7% and +17.6% out-of-sample R² vs no change at 3 and 6 months. It beat time-shifted copies of itself and the best of 57 noise predictors. But it's a mining-era effect (pre-merge +15.7% at 3 months, post-merge +0.2%), and it doesn't pass Benjamini-Hochberg across all 57 tests (q = 0.44).
- Waiting 3 months with a fixed budget was a coin flip if waiting is free (it paid off in 51-56% of months) and paid off in 25-38% of months once a month without the card costs 2% of its price. No timing rule beat buying now by more than about 1%.
- New launches didn't make the previous generation cheaper. A year after a launch the old cards were up 23%, against 13% for other cards, and placebo dates show a gap that size 14% of the time.
- Reverse test: holding NVIDIA + AMD only when GPU prices rose over the last 3 months cut the max drawdown from -61% to -26% but lowered the Sharpe ratio (0.96 vs 1.19). Alpha about 7%/yr, t = 1.1. The best of 9 variants (t = 2.3) is matched by time-shifted signals 12% of the time.
- November averages about 1% below trend (noise). October is the cheapest month on average (-5.6%), but a wait-for-fall rule still lost money.

## How it works

1. PassMark's GPU list shows each card's lowest current retail price next to its G3D Mark score. The Wayback Machine has saved copies of that page going back years. The notebook downloads two copies a month and reads the price table.
2. Prices become a monthly price per card, with guards for stale and glitched prices that only look backward in time.
3. The main index is dollars per 1,000 G3D Mark points for the three best-value cards launched in the last 36 months. Two other indexes (all cards, and a chained same-card index) are there for comparison.
4. Forecasts are walk-forward: at each month a model is fit only on data available then, and scored 1, 3 and 6 months later against "no change". Out-of-sample R², MAE/RMSE, Clark-West or Diebold-Mariano tests, BH q-values.
5. Placebos: noise predictors, the best of 57 noise predictors, circular time shifts of the real predictors, and block-bootstrap intervals.
6. The buy-or-wait simulation uses live prices only, four budgets and a range of waiting costs.

## Run it

```
pip install -r requirements.txt
jupyter notebook gpu_price_model_v7.ipynb
```

No API keys. The first run downloads about 290 archived pages from the Wayback Machine (slow, it pauses between requests) plus stock prices from Yahoo Finance and the T-bill rate from FRED. Everything is cached in `data/`, which isn't in this repo. Tables go to `outputs/` and figures to `figs/`. The last cell prints a summary.

Because the notebook uses the last complete month, rerunning it later gives different numbers from the video.

## Data

- PassMark Software, videocardbenchmark.net GPU list (prices and G3D Mark), via the Internet Archive's Wayback Machine
- Yahoo Finance via yfinance: Micron, SK hynix, Samsung, Nanya, NVIDIA, AMD, S&P 500, Bitcoin, exchange rates
- FRED: 3-month T-bill rate (TB3MS)
- Retail DRAM prices: John C. McCallum's memory price series (Stanford-hosted CSV)

The raw archived pages and per-card price tables aren't included. Run the notebook to rebuild them.

## Limits

- G3D Mark is one synthetic score. It ignores ray tracing, DLSS/FSR and VRAM, and each card's current score is used for every month.
- PassMark's price is the lowest it found that day, which can be a third-party seller. Two snapshots a month can miss a one-day sale.
- Memory versions of the same card (8 GB vs 16 GB) are pooled into one model.
- Launch months were entered by hand.
- Ten years includes only two big shortage episodes (2017-18 and 2021), so rare events have little history.
- The analysis went through several versions on the same data, so treat the tests as exploratory.

## About the code

I built this with a lot of help from Claude (Anthropic's AI). I checked the results and the logic, but if you find a bug, open an issue and I'll fix it and pin the correction under the video.

Not financial advice.

MIT license.
