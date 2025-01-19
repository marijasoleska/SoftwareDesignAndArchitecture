import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras._tf_keras.keras.layers import LSTM, Dense, Dropout
from keras._tf_keras.keras.models import Sequential


class LSTMPredictor:
    def __init__(self, window_size=60):
        self.window_size = window_size
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def predict(self, data: pd.DataFrame) -> dict:
        try:
            # Prepare data
            X, y = self._prepare_data(data)

            # Split data
            split_idx = int(len(X) * 0.7)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]

            # Build and train model
            model = self._build_model((X_train.shape[1], 1))
            model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=0)

            # Make predictions
            predictions = model.predict(X_test)
            predictions = self.scaler.inverse_transform(predictions)
            actual = self.scaler.inverse_transform(y_test.reshape(-1, 1))

            return {
                'predictions': predictions.tolist(),
                'actual': actual.tolist(),
                'rmse': float(np.sqrt(np.mean((predictions - actual) ** 2)))
            }

        except Exception as e:
            raise ValueError(f"Error in LSTM prediction: {str(e)}")

    def _prepare_data(self, data: pd.DataFrame):
        scaled_data = self.scaler.fit_transform(data[['Last trade price']].values)

        X, y = [], []
        for i in range(self.window_size, len(scaled_data)):
            X.append(scaled_data[i - self.window_size:i, 0])
            y.append(scaled_data[i, 0])

        return np.array(X), np.array(y)

    def _build_model(self, input_shape):
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model