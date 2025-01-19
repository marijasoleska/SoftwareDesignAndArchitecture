## Overview
This project is a web application designed to analyze and predict stock market trends using a combination of technical analysis, fundamental analysis, and machine learning techniques.

The application meets the functional and non-functional requirements outlined in the **Software Requirements Specification (SRS)** submitted in Homework 1. It provides an intuitive interface for exploring historical stock data, calculating indicators, analyzing sentiment, and forecasting future prices.

## Preview of the Main Functionalities of the App
[![Watch the Demo Video](https://via.placeholder.com/560x315?text=Demo+Video)](https://vimeo.com/1048311428)

## Features

### 1. Technical Analysis 
- Implements key technical indicators to analyze stock trends:
  - **Oscillators**: RSI, MACD, Stochastic Oscillator, etc.
  - **Moving Averages (MA)**: SMA, EMA, etc.
- Generates trading signals (**Buy**, **Sell**, **Hold**) based on:
  - **Short-Term Trends**: 1-day intervals.
  - **Medium-Term Trends**: 1-week intervals.
  - **Long-Term Trends**: 1-month intervals.

### 2. Fundamental Analysis 
- **Sentiment Analysis**:
  - Uses **Natural Language Processing (NLP)** to evaluate sentiment (positive or negative) of news articles.
  - Extracts relevant financial news from the **Macedonian Stock Exchange** website.
- **Decision Recommendations**:
  - **Positive Sentiment**: Suggests buying stocks.
  - **Negative Sentiment**: Suggests selling stocks.

### 3. LSTM Stock Price Prediction 
- **Machine Learning Implementation**:
  - Trains an **LSTM (Long Short-Term Memory)** network using historical stock price data.
- **Model Performance**:
  - Splits data into training (70%) and validation (30%) sets.
  - Evaluates the model using metrics such as Mean Squared Error (MSE) and Root Mean Squared Error (RMSE).
- **Prediction Output**:
  - Forecasts future stock prices with high accuracy.
## Status

This project is currently under development. Errors are being resolved, and the code is being refactored to enhance quality. Features and functionalities are gradually being implemented in an incremental and structured manner.


## Authors

- **Marija Soleska** 
- **Angela Mitrevska** 
- **Marija Pavlichkovska** 

