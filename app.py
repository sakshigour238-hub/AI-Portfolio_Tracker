import gradio as gr
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression

# Sample Investment Portfolio
portfolio = pd.DataFrame({
    "Asset": ["TCS", "Infosys", "Reliance", "HDFC Bank"],
    "Quantity": [5, 10, 4, 8],
    "Buy Price": [3500, 1500, 2500, 1600],
    "Current Price": [3800, 1650, 2700, 1700]
})


# Calculate Portfolio
def calculate_portfolio(df):
    df = pd.DataFrame(df).copy()

    required = ["Asset", "Quantity", "Buy Price", "Current Price"]

    if not all(col in df.columns for col in required):
        return pd.DataFrame(columns=required + [
            "Invested", "Current Value", "Profit/Loss"
        ])

    for col in ["Quantity", "Buy Price", "Current Price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=required)

    df = df[
        (df["Quantity"] > 0) &
        (df["Buy Price"] >= 0) &
        (df["Current Price"] >= 0)
    ].copy()

    df["Invested"] = df["Quantity"] * df["Buy Price"]
    df["Current Value"] = df["Quantity"] * df["Current Price"]
    df["Profit/Loss"] = df["Current Value"] - df["Invested"]

    return df


# Portfolio Analysis
def analyze_portfolio(df):
    df = calculate_portfolio(df)

    if df.empty:
        return "Please add valid investments."

    invested = df["Invested"].sum()
    current = df["Current Value"].sum()
    profit = current - invested

    if profit > 0:
        status = "Your portfolio is in profit! 📈"
    elif profit < 0:
        status = "Your portfolio is currently at a loss. ⚠️"
    else:
        status = "Your portfolio is balanced."

    best_asset = df.loc[
        df["Profit/Loss"].idxmax(), "Asset"
    ]

    analysis = f"""
# 📊 Your Portfolio Analysis

### {status}

| Financial Details | Amount |
|---|---:|
| Total Investment | ₹{invested:,.2f} |
| Current Value | ₹{current:,.2f} |
| Profit/Loss | ₹{profit:,.2f} |

### 🏆 Best Performing Asset
*{best_asset}*

Calculations use the prices entered in the portfolio.
"""

    return analysis


# Machine Learning Prediction
# Synthetic historical prices for educational demonstration
historical_prices = {
    "TCS": [3400, 3450, 3500, 3550, 3650, 3800],
    "Infosys": [1400, 1450, 1480, 1520, 1600, 1650],
    "Reliance": [2400, 2450, 2500, 2550, 2650, 2700],
    "HDFC Bank": [1500, 1540, 1580, 1620, 1660, 1700]
}


def predict_price(asset):
    prices = np.array(historical_prices[asset])

    X = np.arange(len(prices)).reshape(-1, 1)
    y = prices

    model = LinearRegression()
    model.fit(X, y)

    future = np.array([[len(prices)]])
    prediction = model.predict(future)[0]

    return f"""
# 🤖 AI Price Prediction

### Asset: {asset}

*Latest Sample Price:* ₹{prices[-1]:,.2f}

*Predicted Next Period Price:* ₹{prediction:,.2f}

### Machine Learning Model
Linear Regression

⚠️ This prediction uses synthetic historical data.
It is for educational purposes only and is not
a reliable real-world stock price forecast.
"""


# Portfolio Visualization
def portfolio_chart(df):
    df = calculate_portfolio(df)

    if df.empty:
        return None

    fig = px.bar(
        df,
        x="Asset",
        y=["Invested", "Current Value"],
        barmode="group",
        title="Investment vs Current Value"
    )

    return fig


# Add New Investment
def add_investment(df, asset, quantity, buy_price, current_price):
    df = pd.DataFrame(df).copy()

    if not asset or not asset.strip():
        raise gr.Error("Please enter an asset name.")

    values = [quantity, buy_price, current_price]

    if any(v is None or not np.isfinite(v) for v in values):
        raise gr.Error("Please enter valid numbers.")

    if quantity <= 0 or buy_price < 0 or current_price < 0:
        raise gr.Error("Quantity must be positive and prices non-negative.")

    new_row = pd.DataFrame({
        "Asset": [asset.strip()],
        "Quantity": [quantity],
        "Buy Price": [buy_price],
        "Current Price": [current_price]
    })

    return pd.concat([df, new_row], ignore_index=True)


# Gradio Website
with gr.Blocks(title="AI Portfolio Tracker") as demo:

    gr.Markdown("""
    # 📈 AI Portfolio Tracker

    ### Smart Investment Analysis & Machine Learning Prediction

    *Developed by Sakshi, Sparsh & Jasmin*
    """)

    with gr.Tab("📊 Portfolio Dashboard"):

        portfolio_table = gr.Dataframe(
            value=portfolio,
            interactive=True,
            label="Your Investments"
        )

        analyze_btn = gr.Button(
            "Analyze Portfolio",
            variant="primary"
        )

        analysis_output = gr.Markdown()

        chart_output = gr.Plot()

        analyze_btn.click(
            fn=analyze_portfolio,
            inputs=portfolio_table,
            outputs=analysis_output
        )

        analyze_btn.click(
            fn=portfolio_chart,
            inputs=portfolio_table,
            outputs=chart_output
        )

    with gr.Tab("➕ Add Investment"):

        asset_name = gr.Textbox(
            label="Asset Name"
        )

        quantity = gr.Number(
            label="Quantity",
            value=1
        )

        buy_price = gr.Number(
            label="Buy Price",
            value=0
        )

        current_price = gr.Number(
            label="Current Price",
            value=0
        )

        add_btn = gr.Button(
            "Add Investment",
            variant="primary"
        )

        add_btn.click(
            fn=add_investment,
            inputs=[
                portfolio_table,
                asset_name,
                quantity,
                buy_price,
                current_price
            ],
            outputs=portfolio_table
        )

    with gr.Tab("🤖 AI Prediction"):

        asset_dropdown = gr.Dropdown(
            choices=list(historical_prices.keys()),
            value="TCS",
            label="Select Asset"
        )

        predict_btn = gr.Button(
            "Predict Price",
            variant="primary"
        )

        prediction_output = gr.Markdown()

        predict_btn.click(
            fn=predict_price,
            inputs=asset_dropdown,
            outputs=prediction_output
        )


# Launch Website
if _ _name_ _ == "_ _main_ _":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860
    )
