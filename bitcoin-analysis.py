import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def fetch_bitcoin_data(start_date=None, end_date=None):
    """
    Fetch Bitcoin price data from Yahoo Finance
    """
    try:
        if not start_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=3740)

        btc = yf.download("BTC-USD", start=start_date, end=end_date, progress=False)

        if btc.empty:
            raise ValueError("No data received from Yahoo Finance")

        print(f"Successfully downloaded {len(btc)} records")
        return btc

    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None


def calculate_power_law(data):
    # Get the first date in our dataset
    start_date = data.index[0]

    # Calculate days since start of data
    days_since_start = np.array(
        [(date - start_date).days for date in data.index], dtype=float
    )

    # Convert data["Close"] to a NumPy array
    close_prices = data["Close"].to_numpy(dtype=float)

    # Compute log_days and log_price as arrays
    log_days = np.log(days_since_start + 1)  # shape: (n,)
    log_price = np.log(close_prices)  # shape: (n,)

    # Ensure they are 1D (they should already be, but just in case)
    log_days = log_days.ravel()
    log_price = log_price.ravel()

    # Create mask using NumPy arrays only
    mask = np.isfinite(log_days) & np.isfinite(log_price)
    mask = mask.ravel()

    # Use the masked arrays in polyfit
    coeffs = np.polyfit(log_days[mask], log_price[mask], 1)
    power = coeffs[0]
    constant = np.exp(coeffs[1])

    # Calculate power law prices and add to data DataFrame
    data["power_law"] = constant * (days_since_start + 1) ** power

    return data, constant, power


def create_bitcoin_dashboard(data):
    """
    Create an interactive dashboard showing Bitcoin moving averages and power law
    """
    if data is None or data.empty:
        print("No data available to create dashboard")
        return None

    # Create figure
    fig = go.Figure()

    # Calculate moving averages
    data["MA7"] = data["Close"].rolling(window=7).mean()
    data["MA25"] = data["Close"].rolling(window=25).mean()
    data["MA99"] = data["Close"].rolling(window=99).mean()

    # Calculate power law
    data, constant, power = calculate_power_law(data)

    # Add moving average lines
    ma_traces = [
        go.Scatter(
            x=data.index,
            y=data["MA7"],
            name="7-day MA",
            line=dict(color="#ff1493", width=2),
            visible=True,
        ),
        go.Scatter(
            x=data.index,
            y=data["MA25"],
            name="25-day MA",
            line=dict(color="#FFFF00", width=2),
            visible=True,
        ),
        go.Scatter(
            x=data.index,
            y=data["MA99"],
            name="99-day MA",
            line=dict(color="#32cd32", width=2),
            visible=True,
        ),
    ]

    # Add power law trace
    power_trace = go.Scatter(
        x=data.index,
        y=data["power_law"],
        name=f"Power Law (Price = {constant:.2e} * days^{power:.3f})",
        line=dict(color="#ff4500", width=2, dash="dot"),
        visible=False,
    )

    # Add all traces
    for trace in ma_traces:
        fig.add_trace(trace)
    fig.add_trace(power_trace)

    # Add buttons for log/linear scale and power law with improved visibility
    updatemenus = [
        dict(
            type="buttons",
            direction="right",
            x=1.05,
            y=1.07,
            showactive=True,
            bgcolor="#2b2b2b",
            bordercolor="#4d4d4d",
            font=dict(color="#FF69B4"),
            buttons=[
                dict(
                    label="Linear",
                    method="relayout",
                    args=[{"yaxis.type": "linear"}],
                ),
                dict(
                    label="Log",
                    method="relayout",
                    args=[{"yaxis.type": "log"}],
                ),
            ],
        ),
        dict(
            type="buttons",
            direction="right",
            x=0.97,
            y=1.07,
            showactive=True,
            bgcolor="#2b2b2b",
            bordercolor="#4d4d4d",
            font=dict(color="#FF69B4"),
            buttons=[
                dict(
                    label="MA View",
                    method="update",
                    args=[{"visible": [True, True, True, False]}],
                ),
                dict(
                    label="Power Law",
                    method="update",
                    args=[{"visible": [False, False, False, True]}],
                ),
            ],
        ),
    ]

    # Update layout with complete dark theme
    fig.update_layout(
        template="plotly_dark",
        title=dict(
            text="Bitcoin Price Analysis",
            x=0.5,
            y=0.95,
            font=dict(color="#00ffff", size=24),
        ),
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#1e1e1e",
        yaxis_title=dict(text="Price (USD)", font=dict(color="#00ffff")),
        xaxis_title=dict(text="Date", font=dict(color="#00ffff")),
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        updatemenus=updatemenus,
        font=dict(color="#00ffff"),
        xaxis=dict(
            gridcolor="#333333",
            zerolinecolor="#333333",
            showline=True,
            linecolor="#333333",
        ),
        yaxis=dict(
            gridcolor="#333333",
            zerolinecolor="#333333",
            showline=True,
            linecolor="#333333",
            type="log",  # Set default to log scale for better power law visualization
        ),
        legend=dict(
            bgcolor="#1e1e1e",
            bordercolor="#333333",
        ),
        margin=dict(l=10, r=10, t=80, b=0, pad=0),
        autosize=True,
    )

    return fig


# Example usage
if __name__ == "__main__":
    # Fetch data
    btc_data = fetch_bitcoin_data()

    if btc_data is not None and not btc_data.empty:
        # Create visualization
        fig = create_bitcoin_dashboard(btc_data)

        if fig:
            # Show the interactive plot
            fig.show()
    else:
        print("Unable to proceed without data")
