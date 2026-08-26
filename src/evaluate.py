"""Hata metrikleri ve tahmin grafiği."""

import numpy as np
from sklearn.metrics import mean_squared_error


def evaluate_model(y_true, y_pred, scaler=None):
    """MSE, RMSE ve dolara çevrilmiş serileri döndürür.

    scaler verilirse inverse_transform uygulanıyor. Yoksa hatalar ölçeklenmiş
    uzayda kalır ve "0.0003 hata" gibi okunması imkansız sayılar çıkar.
    """
    y_true = np.asarray(y_true).reshape(-1, 1)
    y_pred = np.asarray(y_pred).reshape(-1, 1)

    if scaler is not None:
        y_true = scaler.inverse_transform(y_true)
        y_pred = scaler.inverse_transform(y_pred)

    mse = mean_squared_error(y_true, y_pred)

    return {
        "mse": float(mse),
        "rmse": float(np.sqrt(mse)),
        "y_true": y_true.flatten(),
        "y_pred": y_pred.flatten(),
    }


def plot_predictions(y_true, y_pred, title="Tahmin vs Gerçek", save_path=None, ax=None):
    # Sadece çizim yapılırken yüklensin
    import matplotlib.pyplot as plt

    kendi_figuru = ax is None
    if kendi_figuru:
        fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(y_true, label="Gerçek")
    ax.plot(y_pred, label="Tahmin")
    ax.set_title(title)
    ax.set_xlabel("Test günü")
    ax.set_ylabel("Fiyat ($)")
    ax.legend()

    if kendi_figuru:
        if save_path:
            fig.savefig(save_path)
        plt.show()
