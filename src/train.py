"""Eğitim döngüsü."""

import time

import torch
from torch import nn


def train_model(model, X_train, y_train, epochs=100, lr=0.01, device="cpu", verbose=True):
    """Modeli eğitir. Geriye model, epoch başına kayıp listesi ve süre döner."""
    model = model.to(device)
    X_train = X_train.to(device)
    y_train = y_train.to(device)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    history = []
    start = time.time()

    # Veri seti birkaç bin örnek, mini-batch'e bölmeye gerek yok.
    # Her epoch'ta tamamı tek seferde geçiyor.
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()

        loss = criterion(model(X_train), y_train)
        loss.backward()
        optimizer.step()

        history.append(loss.item())

        if verbose and (epoch + 1) % max(1, epochs // 10) == 0:
            print(f"Epoch {epoch + 1}/{epochs} - Loss: {loss.item():.6f}")

    elapsed = time.time() - start
    if verbose:
        print(f"Training completed in {elapsed:.2f}s")

    return model, history, elapsed
