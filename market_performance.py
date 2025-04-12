"""
USAGE: On the command line,
    streamlit run 

This launches a browser app

Based on Vince L.'s app https://s-and-p-performance.streamlit.app/
"""

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, date
import plotly.graph_objects as go
from pathlib import Path

TICKERS = [
    "^GSPC",   # S&P 500
    "^DJI",    # Dow Jones Industrial Average
    "^IXIC",   # NASDAQ Composite
    "^RUT",    # Russell 2000
    "^NYA",    # NYSE Composite
    "^VIX",    # Volatility Index (not a price index, but useful)
    "^STOXX50E",  # Euro Stoxx 50 (Europe)
    "^FTSE",   # FTSE 100 (UK)
    "^N225",   # Nikkei 225 (Japan)
    "^HSI",    # Hang Seng Index (Hong Kong)
    "^BVSP",   # Bovespa (Brazil)
    "^AXJO",   # ASX 200 (Australia)
    "^SSEC",   # Shanghai Composite (China)
    "^GDAXI",  # DAX (Germany)
    "^FCHI"    # CAC 40 (France)
]
# Define presidents and their inauguration/event dates
PERIODS = {
    #Presidents
    "Donald Trump (2025)": datetime(2025, 1, 20),
    "Joe Biden (2021)": datetime(2021, 1, 20),
    "Donald Trump (2017)": datetime(2017, 1, 20),
    "Barack Obama (2009)": datetime(2009, 1, 20),
    "George W. Bush (2001)": datetime(2001, 1, 20),
    "Bill Clinton (1993)": datetime(1993, 1, 20),
    "George H. W. Bush (1989)": datetime(1989, 1, 20),
    "Ronald Reagan (1981)": datetime(1981, 1, 20),
    "Jimmy Carter (1977)": datetime(1977, 1, 20),
    "Gerald Ford (1974)": datetime(1974, 8, 9),
    "Richard Nixon (1969)": datetime(1969, 1, 20),
    "Lyndon B. Johnson (1963)": datetime(1963, 11, 22),
    "John F. Kennedy (1961)": datetime(1961, 1, 20),
    "Dwight D. Eisenhower (1953)": datetime(1953, 1, 20),
    "Harry S. Truman (1945)": datetime(1945, 4, 12),
    "FDR 1 (1933–1937)": datetime(1933, 3, 4),
    "FDR 2 (1937–1941)": datetime(1937, 1, 20),
    "FDR 3 (1941–1945)": datetime(1941, 1, 20),
    "FDR 4 (1945)": datetime(1945, 1, 20),
    "Herbert Hoover (1929)": datetime(1929, 3, 4),
    
    #Notable Periods:
    "Black Thursday (10/24/1929)": datetime(1929, 10, 23),
    "Black Monday (10/19/1987)": datetime(1987, 10, 16), #Black Monday, the October 1987 stock market crash, was caused by a complex interplay of factors, including a strong bull market overdue for a correction, the rise of computer-driven trading, and portfolio insurance strategies. While no single event triggered the crash, these elements combined to create a chain reaction of panic selling that led to the largest one-day stock market decline in history.
    "Pandemic (2/19/2020)":datetime(2020,3,10),
    "Liberation Day (4/2/2025)": datetime(2025, 4, 2),
}

PERIOD_DURATIONS = {
    #Presidents
    "Donald Trump (2025)": (datetime.today() - datetime(2025, 1, 20)).days,
    "Joe Biden (2021)": (datetime(2025, 1, 20) - datetime(2021, 1, 20)).days,
    "Donald Trump (2017)": (datetime(2021, 1, 20) - datetime(2017, 1, 20)).days,
    "Barack Obama (2009)": (datetime(2017, 1, 20) - datetime(2009, 1, 20)).days,
    "George W. Bush (2001)": (datetime(2009, 1, 20) - datetime(2001, 1, 20)).days,
    "Bill Clinton (1993)": (datetime(2001, 1, 20) - datetime(1993, 1, 20)).days,
    "George H. W. Bush (1989)": (datetime(1993, 1, 20) - datetime(1989, 1, 20)).days,
    "Ronald Reagan (1981)": (datetime(1989, 1, 20) - datetime(1981, 1, 20)).days,
    "Jimmy Carter (1977)": (datetime(1981, 1, 20) - datetime(1977, 1, 20)).days,
    "Gerald Ford (1974)": (datetime(1977, 1, 20) - datetime(1974, 8, 9)).days,
    "Richard Nixon (1969)": (datetime(1974, 8, 9) - datetime(1969, 1, 20)).days,
    "Lyndon B. Johnson (1963)": (datetime(1969, 1, 20) - datetime(1963, 11, 22)).days,
    "John F. Kennedy (1961)": (datetime(1963, 11, 22) - datetime(1961, 1, 20)).days,
    "Dwight D. Eisenhower (1953)": (datetime(1961, 1, 20) - datetime(1953, 1, 20)).days,
    "Harry S. Truman (1945)": (datetime(1953, 1, 20) - datetime(1945, 4, 12)).days,
    "FDR 1 (1933–1937)": (datetime(1937, 1, 20) - datetime(1933, 3, 4)).days,
    "FDR 2 (1937–1941)": (datetime(1941, 1, 20) - datetime(1937, 1, 20)).days,
    "FDR 3 (1941–1945)": (datetime(1945, 1, 20) - datetime(1941, 1, 20)).days,
    "FDR 4 (1945)": (datetime(1945, 4, 12) - datetime(1945, 1, 20)).days,
    "Herbert Hoover (1929)": (datetime(1933, 3, 4) - datetime(1929, 3, 4)).days,

    #Notable Periods:
    "Black Thursday (10/24/1929)": 30,
    "Black Monday (10/19/1987)": 30,
    "Pandemic (2/19/2020)":30,
    "Liberation Day (4/2/2025)": (datetime.today() - datetime(2025, 4, 2)).days,
}
def download_and_cache_cpi(cache_path="cpi_cache.csv",expected_day_new_data = 15):
    def is_cpi_data_fresh(cpi_df):
        def expected_latest_cpi_date(today=None):
            """
            Returns the most recent CPI date that should be available as of today.
            CPI is released mid-month for the prior month.
            """
            if today is None:
                today = date.today()
            if today.day > expected_day_new_data:
                return date(today.year, today.month, 1)
            else:
                # If before the expected date (e.g. 10th or 15th), last available CPI is for two months ago
                if today.month == 1:
                    return date(today.year - 1, 12, 1)
                else:
                    return date(today.year, today.month - 1, 1)
        latest_expected = pd.to_datetime(expected_latest_cpi_date())
        return latest_expected in cpi_df.index
    
    def download_and_cache_combined_cpi():
        # Step 1: Your BLS early data (annual CPI, Jan 1 for each year)
        early_data = {
            "1913-01-01": 9.9, "1914-01-01": 10, "1915-01-01": 10.1, "1916-01-01": 10.9,
            "1917-01-01": 12.8, "1918-01-01": 15, "1919-01-01": 17.3, "1920-01-01": 20,
            "1921-01-01": 17.9, "1922-01-01": 16.8, "1923-01-01": 17.1, "1924-01-01": 17.1,
            "1925-01-01": 17.5, "1926-01-01": 17.7, "1927-01-01": 17.4, "1928-01-01": 17.2,
            "1929-01-01": 17.2, "1930-01-01": 16.7, "1931-01-01": 15.2, "1932-01-01": 13.6,
            "1933-01-01": 12.9, "1934-01-01": 13.4, "1935-01-01": 13.7, "1936-01-01": 13.9,
            "1937-01-01": 14.4, "1938-01-01": 14.1, "1939-01-01": 13.9, "1940-01-01": 14,
            "1941-01-01": 14.7, "1942-01-01": 16.3, "1943-01-01": 17.3, "1944-01-01": 17.6,
            "1945-01-01": 18, "1946-01-01": 19.5
        }

        early_cpi = pd.Series(early_data).rename("CPI").astype(float)
        early_cpi.index = pd.to_datetime(early_cpi.index)

        # Step 2: Download CPI from FRED (starts in 1947)
        fred_cpi = web.DataReader('CPIAUCSL', 'fred', '1947-01-01')
        fred_cpi.columns = ["CPI"]

        # Step 3: Combine early and FRED data
        combined_cpi = pd.concat([early_cpi, fred_cpi])
        combined_cpi = combined_cpi[~combined_cpi.index.duplicated()]  # ensure no duplicate indices

        # Step 4: Save to CSV
        combined_cpi = combined_cpi.rename(columns={"CPI": "CPIAUCSL"})
        combined_cpi.index.name = "DATE"
        combined_cpi.to_csv(cache_path)
        print(f"Saved combined CPI data to {cache_path}")

        return combined_cpi

    cache_file = Path(cache_path)
    if cache_file.exists():
        cpi = pd.read_csv(cache_file, parse_dates=["DATE"], index_col="DATE")
    else:
        cpi = pd.DataFrame()

    if not is_cpi_data_fresh(cpi):
        print("CPI data is outdated or missing. Downloading latest from FRED...")
        return download_and_cache_combined_cpi()
    else:
        return cpi


CPI = download_and_cache_cpi()


def get_latest_cpi_on_or_before(date, cpi_series=CPI):
    """
    Returns the CPI value (float) for the latest date on or before the given date.
    Assumes cpi_series is a pandas Series (not DataFrame) indexed by date.
    """
    return float(cpi_series.loc[cpi_series.index <= date].iloc[-1])

def get_inflation_adjusted_data(prices_or_df, start):
    """
    Adjusts for inflation using CPI at the given base 'start' date.
    
    If passed a Series: returns a Series of real prices.
    If passed a DataFrame with a 'Close' column: returns a DataFrame with 'Real Close' and 'Real Return'.

    Parameters:
    - prices_or_df: pd.Series or pd.DataFrame with datetime index
    - start: base date for CPI adjustment

    Returns:
    - Adjusted Series or DataFrame depending on input
    """
    cpi_base = get_latest_cpi_on_or_before(pd.to_datetime(start))

    if isinstance(prices_or_df, pd.Series):
        real_prices = prices_or_df.index.map(
            lambda d: prices_or_df.loc[d] * (cpi_base / get_latest_cpi_on_or_before(d))
        )
        return pd.Series(real_prices.values, index=prices_or_df.index, name="Real Price")

    elif isinstance(prices_or_df, pd.DataFrame) and "Close" in prices_or_df.columns:
        df = prices_or_df.copy()
        df["Real Close"] = df.index.map(
            lambda d: df.loc[d, "Close"] * (cpi_base / get_latest_cpi_on_or_before(d))
        )
        df["Real Return"] = df["Real Close"].pct_change()
        return df

    else:
        raise ValueError("Input must be a Series or a DataFrame containing a 'Close' column.")


def get_earliest_start_date(selected_periods):
    """
    Returns the earliest start date among selected periods.

    Parameters:
    - selected_presidents: list of period labels (keys in the PERIODS dict)

    Returns:
    - datetime.date representing the earliest start
    """
    if not selected_periods:
        return None  # or raise ValueError("No periods selected.")

    return min(PERIODS[p] for p in selected_periods)

def do_st_plot():
    st.title("Stock Market Performance by Historical Period")

    selected_presidents = st.multiselect(
        "Select periods to compare:",
        options=list(PERIODS.keys()),
    )
    selected_tickers = st.multiselect(
        "Select tickers to compare:",
        options=TICKERS,
    )
   
    @st.cache_data
    def get_selected_ticker_data(ticker):
        return yf.download(ticker, auto_adjust=True)["Close"]

   
    all_series = {}
    adjust_for_inflation = st.toggle("Adjust for inflation", value=False)
    base_inflation_date = get_earliest_start_date(selected_presidents)

    for selected_ticker in selected_tickers:
        ticker_data = get_selected_ticker_data(selected_ticker)
        use_key = "Adj" if adjust_for_inflation else selected_ticker
        for pres in selected_presidents:
 
            start = PERIODS[pres]
            max_days = int(PERIOD_DURATIONS[pres])
            end = start + timedelta(days=max_days)

            data = ticker_data.loc[(ticker_data.index >= start) & (ticker_data.index <= end)].copy()
            data = data[:max_days]
            if data.empty:
                st.warning(f"No data for {selected_ticker} during {pres}. Skipping.")
                continue  
            data["Adj"] = get_inflation_adjusted_data(data[selected_ticker],base_inflation_date)
            data = data.reset_index()
            data["Day"] = range(len(data))  # align by trading day index
            data["% Change"] = data[use_key]/data[use_key].iloc[0]*100-100
            all_series[f"{pres}-{selected_ticker}"] = data


    fig = go.Figure()

    for pres, data in all_series.items():
        fig.add_trace(go.Scatter(
            x=data["Day"],
            y=data["% Change"],
            mode='lines',
            name=pres,
            customdata=data[["Date"]].apply(lambda row: [row["Date"].strftime("%Y-%m-%d")], axis=1),
            hovertemplate='Day: %{x}, Date: %{customdata[0]}, Change: %{y:.2f}%, ' + pres + '<extra></extra>'
        ))
    suffix = f" ({'Inflation Adjusted' if adjust_for_inflation else 'Nominal'})"
    fig.update_layout(
        title=f"Performance During Historical Periods" + suffix,
        xaxis_title="Trading Days After Event",
        yaxis_title=f"% Change",
        hovermode='x unified',
        legend_title="President"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption("1927–1957: S&P 500 reconstructed data (based on S&P 90 and similar). Data sourced from Yahoo Finance using yfinance.")
    st.caption("Streamlit app developed by JP Lawner with assistance from ChatGPT 4o, based on original code by Vince L.")
     



if __name__ == "__main__":
    do_st_plot()
