from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import math
from keras._tf_keras.keras.layers import LSTM, Dense, Dropout
from keras._tf_keras.keras.models import Sequential
import matplotlib.pyplot as plt
from scraper import fetch_data_for_all_companies_threaded
from technical_analysis import perform_technical_analysis

app = Flask(__name__)
UPLOAD_FOLDER = './data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'scrape':
            fetch_data_for_all_companies_threaded()
            return redirect(url_for('index'))

        company = request.form.get('company')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')

        if company:
            file_path = os.path.join(UPLOAD_FOLDER, f"{company}.csv")
            if os.path.exists(file_path):
                data = preprocess_data(file_path)

                if date_from and date_to:
                    date_from = pd.to_datetime(date_from)
                    date_to = pd.to_datetime(date_to)
                    data = data[(data['Date'] >= date_from) & (data['Date'] <= date_to)]

                if data.empty:
                    return render_template(
                        'index.html',
                        error="No data available for the selected date range.",
                        companies=get_companies()
                    )

                if action == 'analyze_table':
                    table_html = data.to_html(index=False, classes='table table-striped')
                    return redirect(url_for(
                        'view_table',
                        company=company,
                        date_from=date_from,
                        date_to=date_to,
                        table=table_html
                    ))
                elif action == 'analyze_technical':
                    analysis_html = perform_technical_analysis(data, company)
                    return render_template(
                        'technical_analysis.html',
                        company=company,
                        analysis=analysis_html
                    )
                elif action == 'analyze_fundamental':
                    recommendation, fundamental_table = perform_fundamental_analysis(data, date_from, date_to)
                    return render_template(
                        'fundamental_analysis.html',
                        company=company,
                        date_from=date_from,
                        date_to=date_to,
                        fundamental_table = fundamental_table,
                        recommendation=recommendation
                    )
                elif action == 'analyze_lstm':
                    lstm_prediction, plot_path = perform_lstm_analysis(data, date_from, date_to, company)
                    return render_template(
                        'lstm_analysis.html',
                        company=company,
                        date_from=date_from,
                        date_to=date_to,
                        plot_path=plot_path,
                        lstm_prediction=lstm_prediction
                    )
            else:
                return render_template(
                    'index.html',
                    error=f"No data found for {company}.",
                    companies=get_companies()
                )

    return render_template('index.html', companies=get_companies())

def preprocess_data(file_path):
    data = pd.read_csv(file_path)
    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y', errors='coerce')

    numeric_cols = ['Last trade price', 'Max', 'Min', 'Avg Price', '%chg.', 'Volume', 'TurnoverBEST_MKD', 'TotalTurnoverMKD']
    for col in numeric_cols:
        data[col] = data[col].replace({',': '', '"': ''}, regex=True).apply(pd.to_numeric, errors='coerce')

    return data

def get_companies():
    return [file.replace('.csv', '') for file in os.listdir(UPLOAD_FOLDER) if file.endswith('.csv')]

@app.route('/view_table', methods=['GET'])
def view_table():
    company = request.args.get('company')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    table_html = request.args.get('table')

    return render_template(
        'view_table.html',
        company=company,
        date_from=date_from,
        date_to=date_to,
        table=table_html
    )

def perform_fundamental_analysis(stock_data, date_from, date_to):
    filtered_data = stock_data[(stock_data['Date'] >= date_from) & (stock_data['Date'] <= date_to)]

    if filtered_data.empty:
        return "No stock data available for the selected date range."

    fundamental_table = filtered_data[['Date', 'Last trade price']].to_html(index=False, classes='table table-striped')

    stock_movement_counter = analyze_stock_movement(filtered_data)

    if stock_movement_counter > 0:
        recommendation = "Buy"
    elif stock_movement_counter < 0:
        recommendation = "Sell"
    else:
        recommendation = "Hold"

    return recommendation, fundamental_table

def analyze_stock_movement(stock_data):
    movement_counter = 0
    for i in range(1, len(stock_data)):
        previous_day_price = stock_data['Last trade price'].iloc[i - 1]
        current_day_price = stock_data['Last trade price'].iloc[i]

        if current_day_price < previous_day_price:
            movement_counter += 1
        elif current_day_price > previous_day_price:
            movement_counter -= 1

    return movement_counter

def preprocess_for_lstm(stock_data, window_size=60):
    from sklearn.preprocessing import MinMaxScaler
    import numpy as np

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(stock_data[['Last trade price']].values)

    X, y = [], []
    for i in range(window_size, len(scaled_data)):
        X.append(scaled_data[i - window_size:i, 0])
        y.append(scaled_data[i, 0])

    if len(X) == 0 or len(y) == 0:
        raise ValueError("Insufficient data for LSTM preprocessing. Consider using a larger date range.")

    X, y = np.array(X), np.array(y)
    print(f"Shape of X before reshaping: {X.shape}")  # Debugging
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))  # Reshape for LSTM input

    return X, y, scaler

def build_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_lstm_model(model, X_train, y_train, epochs=20, batch_size=32):
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.2)
    return model

def predict_lstm(model, X_test, scaler):
    predicted_prices = model.predict(X_test)
    return scaler.inverse_transform(predicted_prices)

def evaluate_lstm_model(y_test, predicted_prices):
    mse = mean_squared_error(y_test, predicted_prices)
    rmse = math.sqrt(mse)
    return rmse

def perform_lstm_analysis(data, date_from, date_to, company, window_size=60):
    try:
        stock_data = data[(data['Date'] >= date_from) & (data['Date'] <= date_to)]
        if stock_data.empty:
            raise ValueError("No stock data available for the selected date range.")

        X, y, scaler = preprocess_for_lstm(stock_data, window_size)

        split_ratio = 0.7
        train_size = int(len(X) * split_ratio)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        model = build_lstm_model((X_train.shape[1], 1))
        model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=1)

        predictions = model.predict(X_test)
        predicted_prices = scaler.inverse_transform(predictions)
        actual_prices = scaler.inverse_transform(y_test.reshape(-1, 1))

        rmse = np.sqrt(np.mean((predicted_prices - actual_prices) ** 2))

        plt.figure(figsize=(10, 6))
        plt.plot(actual_prices, label='Actual Prices', color='blue')
        plt.plot(predicted_prices, label='Predicted Prices', color='orange')
        plt.title(f"Stock Price Prediction ({company})")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.legend()
        plt.grid()

        plot_path = f'./static/{company}_lstm_plot.png'
        plt.savefig(plot_path)
        plt.close()

        return f"LSTM RMSE: {rmse:.2f}", plot_path

    except ValueError as e:
        return str(e), None

if __name__ == '__main__':
    app.run(debug=True)