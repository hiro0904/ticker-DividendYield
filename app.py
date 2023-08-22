# 環境構築
import pandas as pd
import yfinance as yf
from datetime import timedelta, datetime
import streamlit as st
import numpy as np
import pytz
import plotly.express as px
import plotly.graph_objects as go


def get_annual_dividends(ticker):
    end_date = pd.Timestamp.now(tz=pytz.UTC)
    start_date = end_date - pd.DateOffset(years=1)
    dividends = yf.Ticker(ticker).dividends.loc[start_date:end_date]
    dividends.index = pd.to_datetime(dividends.index).tz_convert(pytz.UTC)  # タイムゾーンを変換
    # st.write(dividends)
    annual_dividend = sum(dividends.values)
    return annual_dividend


def closed_price(ticker):
    end_date = pd.Timestamp.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=1)

    ticker_data = yf.download(ticker, start=start_date, end=end_date)
    if ticker_data.empty:
        st.write(f"No data found for {ticker} on {start_date}.")
        return None

    closing_price = ticker_data["Close"].iloc[0]
    return closing_price


def checkYield(ticker, dividendYield):
    value = closed_price(ticker)
    annualDividends = get_annual_dividends(ticker)
    basePrice = annualDividends * 100 / dividendYield
    nowYield = annualDividends * 100 / value
    st.header(
        f"{ticker}の終値:{value:.2f} 現在の配当利回り:{nowYield:.2f}% 配当利回り{dividendYield}%の購入基準価格:{basePrice:.2f} "
    )


def get_historical_data(ticker):
    stock = yf.Ticker(ticker)
    # end_date = datetime.now() - timedelta(days=1)
    # start_date = end_date - pd.DateOffset(years=5)
    stock_data = yf.download(ticker, period="max")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=stock_data.index, y=stock_data["Close"], mode="lines", name="Close Price",
        )
    )
    fig.update_layout(title=f"{ticker}の過去の株価チャート", xaxis_title="日付", yaxis_title="株価")
    st.plotly_chart(fig)


def main():
    st.title("配当利回りの価格検索")
    st.header("ティッカーと配当利回りから基準価格を計算します")
    ticker = st.text_input("銘柄コードを入力してください ", "VYM")
    dividendYield = st.number_input("配当利回りを入力して下さい", 3.20)
    if dividendYield > 100 or dividendYield < 0:
        st.warning("配当利回りが正しくありません。0から100の間で入力して下さい")
        dividendYield = 3.00
    value = closed_price(ticker)
    st.header(f"{ticker}の終値の価格は{value:.2f}USD")
    get_historical_data(ticker)
    annualDividends = get_annual_dividends(ticker)

    st.subheader(f"指定されたシンボルの年間配当は{annualDividends:.2f}USD")
    basePrice = annualDividends * 100 / dividendYield
    st.header(f"購入基準価格は{basePrice:.2f}")
    exampleYield = np.arange(2.0, 10 + 0.1, 0.1)
    examplePrice = annualDividends * 100 / exampleYield
    fig = px.scatter(x=exampleYield, y=examplePrice, labels={"x": "配当利回り", "y": "基準価格"})
    st.plotly_chart(fig)
    st.text("-------------------------")
    st.header("自分用 watch銘柄の現在株価、利回り、購入基準価格")
    checkYield("VYM", 3.2)
    checkYield("SPYD", 5.5)
    checkYield("VIG", 2)
    checkYield("VGLT", 3.5)
    checkYield("PFFD", 6.0)
    checkYield("HYG", 5.2)
    checkYield("VDC", 2.5)


if __name__ == "__main__":
    main()
