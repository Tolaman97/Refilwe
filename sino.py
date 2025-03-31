import streamlit as st
import yfinance as yf


st.write("""simple stockk price app"

         show price stock closing and value price of google

           """)
tickersymbol = "AAPL"
tickerData = yf.Ticker(tickersymbol)
tickerDF = tickerData.history(period =   "1d"  , start = "2010-5-31"  , end = "2022-5-30" )
st.line_chart(tickerDF.Close)
st.line_chart(tickerDF.Volume)
 