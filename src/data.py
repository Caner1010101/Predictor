"""Veri indirme, ölçekleme ve pencereleme."""

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler

FEATURE_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]
TARGET_COLUMN = "Close"

# Buraya sabit bir "ilk 10" listesi yazmadım, sıralama zamanla değişiyor.
# fetch_market_caps() bu havuzun güncel değerlerini çekip kendisi sıralıyor.
MEGA_CAP_CANDIDATES = [
    "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "AVGO", "TSLA", "BRK-B",
    "TSM", "LLY", "WMT", "JPM", "V", "ORCL", "MA", "NFLX", "XOM", "COST", "JNJ",
]


def download_data(ticker="MSFT", start="2014-01-01", end="2026-01-01", save_path=None):
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)

    # Tek hisse istesen bile yfinance bazen MultiIndex sütun döndürüyor
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    if save_path:
        df.to_csv(save_path, index=False)

    return df


def scale_features(df, feature_columns=None, feature_range=(-1, 1)):
    """Girdi sütunlarını [-1, 1] aralığına sıkıştırır."""
    if feature_columns is None:
        feature_columns = FEATURE_COLUMNS

    scaler = MinMaxScaler(feature_range=feature_range)
    scaled = scaler.fit_transform(df[feature_columns].to_numpy())

    # Her sütun kendi min/max'ına göre ölçekleniyor, o yüzden Volume (~1e8)
    # fiyatları (~1e2) ezmiyor.
    return scaled, scaler


def scale_target(df, target_column=TARGET_COLUMN, feature_range=(-1, 1)):
    """Hedef sütun için ayrı scaler.

    Bu ayrı olmak zorunda. Model tek sayı üretiyor ve onu dolara geri çevirmek
    gerekiyor; beş sütuna fit edilmiş scaler hangi sütunun tersini alacağını
    bilemez.
    """
    scaler = MinMaxScaler(feature_range=feature_range)
    return scaler.fit_transform(df[[target_column]].to_numpy()), scaler


def create_sliding_windows(features, target, lookback=20):
    """20 günlük dilimleri 21. günün hedefiyle eşler.

    X -> (örnek, lookback, özellik), y -> (örnek, 1)
    """
    X, y = [], []

    for i in range(len(features) - lookback):
        X.append(features[i:i + lookback])
        y.append(target[i + lookback])

    return np.array(X), np.array(y)


def train_test_split_sequences(X, y, train_ratio=0.8):
    # Zaman serisi, karıştırmıyoruz. İlk %80 eğitim, kalanı test.
    split = int(len(X) * train_ratio)
    return X[:split], X[split:], y[:split], y[split:]


def fetch_market_caps(tickers=None, top_n=10):
    """Adayların güncel piyasa değerini çekip sıralar. Yavaş, önbelleğe alın."""
    if tickers is None:
        tickers = MEGA_CAP_CANDIDATES

    rows = []
    for symbol in tickers:
        try:
            info = yf.Ticker(symbol).info
        except Exception:
            # Tek sembol düşerse listenin tamamı bozulmasın
            continue

        cap = info.get("marketCap")
        if not cap:
            continue

        rows.append({
            "ticker": symbol,
            "name": info.get("shortName") or info.get("longName") or symbol,
            "market_cap": cap,
        })

    rows.sort(key=lambda r: -r["market_cap"])
    return rows[:top_n]


def format_market_cap(value):
    """3_640_000_000_000 -> '$3.64T'"""
    if value >= 1e12:
        return f"${value / 1e12:.2f}T"
    if value >= 1e9:
        return f"${value / 1e9:.0f}B"
    return f"${value / 1e6:.0f}M"
