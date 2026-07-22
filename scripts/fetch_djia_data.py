"""
fetch_djia_data.py
==================
Downloads end-of-day OHLCV data for all 30 DJIA constituent stocks
from Yahoo Finance using the yfinance library and saves them to the
Data/ directory in the CSV format expected by the D3.js charts.

Usage:
    pip install yfinance pandas
    python scripts/fetch_djia_data.py

Optional arguments:
    --start     Start date (default: 2014-02-21)
    --end       End date   (default: 2019-02-20)
    --output    Output directory (default: ./Data)

To fetch the original dataset covered by the project:
    python scripts/fetch_djia_data.py --start 2014-02-21 --end 2019-02-20

To fetch the most recent 5-year window:
    python scripts/fetch_djia_data.py --start 2020-01-01 --end 2025-01-01
"""

import argparse
import os
import sys
import time

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print("Required packages not found. Install them with:")
    print("    pip install yfinance pandas")
    sys.exit(1)


# All 30 DJIA constituents as of the original dataset (Feb 2014 – Feb 2019)
DJIA_TICKERS = [
    "AAPL",  # Apple Inc.
    "AXP",   # American Express
    "BA",    # Boeing
    "CAT",   # Caterpillar
    "CSCO",  # Cisco Systems
    "CVX",   # Chevron
    "DIS",   # Walt Disney
    "DWDP",  # DowDuPont (merged Sep 2017 — data only from that date)
    "GS",    # Goldman Sachs
    "HD",    # Home Depot
    "IBM",   # IBM
    "INTC",  # Intel
    "JNJ",   # Johnson & Johnson
    "JPM",   # JPMorgan Chase
    "KO",    # Coca-Cola
    "MCD",   # McDonald's
    "MMM",   # 3M
    "MRK",   # Merck & Co.
    "MSFT",  # Microsoft
    "NKE",   # Nike
    "PFE",   # Pfizer
    "PG",    # Procter & Gamble
    "TRV",   # Travelers
    "UNH",   # UnitedHealth Group
    "UTX",   # United Technologies (merged into Raytheon 2020)
    "V",     # Visa
    "VZ",    # Verizon Communications
    "WBA",   # Walgreens Boots Alliance
    "WMT",   # Walmart
    "XOM",   # ExxonMobil
]


def fetch_ticker(ticker: str, start: str, end: str, output_dir: str) -> bool:
    """
    Downloads OHLCV data for a single ticker and saves to CSV.
    Returns True on success, False on failure.

    Output CSV schema matches the format expected by the D3.js charts:
        date, open, high, low, close, volume, unadjustedVolume,
        change, changePercent, vwap, label, changeOverTime
    """
    try:
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)

        if df.empty:
            print(f"  [{ticker}] WARNING: No data returned (ticker may be delisted)")
            return False

        # Flatten MultiIndex columns if present (yfinance ≥ 0.2.x)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]

        # Compute change and changePercent
        df["change"] = df["close"].diff().round(4)
        df["changePercent"] = (df["close"].pct_change() * 100).round(4)
        df["changeOverTime"] = (df["close"] / df["close"].iloc[0] - 1).round(10)

        # Add placeholder columns to match original schema
        df["unadjustedVolume"] = df["volume"]
        df["vwap"] = ((df["high"] + df["low"] + df["close"]) / 3).round(4)
        df["label"] = df["date"].dt.strftime("%b %-d, %y")

        # Reorder columns to match original CSV schema
        output_cols = [
            "date", "open", "high", "low", "close", "volume",
            "unadjustedVolume", "change", "changePercent", "vwap",
            "label", "changeOverTime",
        ]
        df = df[output_cols].fillna(0)

        # Format date as YYYY-MM-DD
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

        output_path = os.path.join(output_dir, f"{ticker}.csv")
        df.to_csv(output_path, index=False)
        print(f"  [{ticker}] ✓  {len(df)} rows → {output_path}")
        return True

    except Exception as e:
        print(f"  [{ticker}] ERROR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download DJIA OHLCV data from Yahoo Finance"
    )
    parser.add_argument(
        "--start", default="2014-02-21",
        help="Start date YYYY-MM-DD (default: 2014-02-21)"
    )
    parser.add_argument(
        "--end", default="2019-02-20",
        help="End date YYYY-MM-DD (default: 2019-02-20)"
    )
    parser.add_argument(
        "--output", default="Data",
        help="Output directory (default: Data/)"
    )
    args = parser.parse_args()

    # Resolve output directory relative to repo root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    output_dir = os.path.join(repo_root, args.output)
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nDJIA Data Fetcher")
    print(f"Period : {args.start} → {args.end}")
    print(f"Tickers: {len(DJIA_TICKERS)}")
    print(f"Output : {output_dir}\n")

    success, failed = 0, []
    for ticker in DJIA_TICKERS:
        result = fetch_ticker(ticker, args.start, args.end, output_dir)
        if result:
            success += 1
        else:
            failed.append(ticker)
        time.sleep(0.3)  # Polite rate limiting

    print(f"\n{'='*50}")
    print(f"Done. {success}/{len(DJIA_TICKERS)} tickers downloaded successfully.")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        print("Note: DWDP (DowDuPont) may not be available — it merged into DOW/DD in 2019.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
