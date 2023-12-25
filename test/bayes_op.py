# Bayesian Optimization
from bayes_opt import BayesianOptimization
import numpy as np
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.callbacks import EarlyStopping

logger_folder = './log'
result_folder = './result'


def LongShortTM(df, param, file_name, time_into_future_prediction):
    def create_sequences(data, n_lags):
        X, y = [], []
        for i in range(n_lags, len(data)):
            X.append(data[i - n_lags:i, 0])
            y.append(data[i, 0])
        return np.array(X), np.array(y)

    # Grouping the data by 1-minute intervals
    df_grouped = df.groupby('timestamp')[param].mean().reset_index()

    # Scaling the param data
    scaler = MinMaxScaler(feature_range=(0, 1))
    cpu_usage_scaled = scaler.fit_transform(df_grouped[[param]].values)

    # Number of lags (sequence length)
    n_lags_lstm = 7

    # Creating sequences
    X, y = create_sequences(cpu_usage_scaled, n_lags_lstm)

    # Splitting the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0)

    # Reshaping input for LSTM model
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

    # LSTM model
    lstm_model = Sequential()
    lstm_model.add(LSTM(units=50, return_sequences=True,
                        input_shape=(X_train.shape[1], 1)))
    lstm_model.add(LSTM(units=50))
    lstm_model.add(Dense(1))

    lstm_model.compile(optimizer='adam', loss='mean_squared_error')

    # Early stopping to avoid overfitting
    early_stopping = EarlyStopping(
        monitor='val_loss', patience=10, restore_best_weights=True)

    # Training the LSTM model
    lstm_model.fit(X_train, y_train, epochs=100, batch_size=32,
                   validation_data=(X_test, y_test), callbacks=[early_stopping], verbose=0)

    mse_raw = lstm_model.evaluate(X_test, y_test, verbose=0)
    print("MSE on test set:", mse_raw)

    # Now with all the data.
    # Preparing the full dataset for training
    X_full, y_full = create_sequences(cpu_usage_scaled, n_lags_lstm)

    # Reshaping input for LSTM model
    X_full = X_full.reshape(X_full.shape[0], X_full.shape[1], 1)

    # LSTM model
    lstm_model_full = Sequential()
    lstm_model_full.add(LSTM(units=50, return_sequences=True,
                        input_shape=(X_full.shape[1], 1)))
    lstm_model_full.add(LSTM(units=50))
    lstm_model_full.add(Dense(1))

    lstm_model_full.compile(optimizer='adam', loss='mean_squared_error')

    # Training the LSTM model on the full dataset
    lstm_model_full.fit(X_full, y_full, epochs=100, batch_size=32, verbose=0)

    def rolling_predictions(model, input_sequence, future_periods):
        current_sequence = input_sequence.copy()
        predictions = []
        for _ in range(future_periods):
            predicted_value = model.predict(
                current_sequence.reshape(1, -1, 1))[0, 0]
            predictions.append(predicted_value)
            current_sequence = np.roll(current_sequence, -1)
            current_sequence[-1] = predicted_value
        return predictions

    # Example of making rolling predictions for the next 5 minutes
    # Use the last sequence from your data as the input sequence
    last_sequence = X[-1]
    future_predictions = rolling_predictions(
        lstm_model_full, last_sequence, time_into_future_prediction)

    # Convert predictions back to original scale
    future_predictions_scaled = scaler.inverse_transform(
        np.array(future_predictions).reshape(-1, 1))

    print(f"Predicted CPU Usage for the next {time_into_future_prediction} minutes:",
          future_predictions_scaled.ravel())

    file_path = f'{logger_folder}/{file_name}_{param}_logs.csv'

    # Convertir el array de NumPy a un DataFrame de Pandas
    log_df = pd.DataFrame(future_predictions_scaled,
                          columns=[
                              param,
                          ])
    log_df['mse'] = mse_raw
    log_df.to_csv(file_path, index=False)

    return future_predictions_scaled


def optimize(file_name, time_into_future_prediction):
    file_path = f'{result_folder}/{file_name}.csv'
    df = pd.read_csv(file_path)

    next_cpu = LongShortTM(df, 'cpu_usage', file_name,
                           time_into_future_prediction)
    next_memory = LongShortTM(
        df, 'memory_usage', file_name, time_into_future_prediction)
    return next_cpu, next_memory
