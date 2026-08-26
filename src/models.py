"""LSTM ve GRU modelleri.

İkisi de aynı iskeleti kullanıyor: RNN katmanı 20 günlük diziyi okuyor, son
zaman adımının çıktısı Linear katmandan geçip tek sayıya iniyor. Tek fark RNN
tipi, böylece karşılaştırma adil oluyor.
"""

import torch.nn as nn


class LSTMModel(nn.Module):
    def __init__(self, input_size=5, hidden_size=32, num_layers=2, output_size=1, dropout=0.0):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # PyTorch tek katmanda dropout verilince uyarı basıyor, o yüzden koşullu
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True,
                            dropout=dropout if num_layers > 1 else 0.0)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # Gizli durum ve hücre durumu, her pencere için sıfırdan.
        # new_zeros -> tensörler x ile aynı cihazda oluşuyor.
        h0 = x.new_zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = x.new_zeros(self.num_layers, x.size(0), self.hidden_size)

        out, _ = self.lstm(x, (h0, c0))

        # 20 adımın hepsi için çıktı geliyor, bize sadece sonuncusu lazım
        return self.fc(out[:, -1, :])


class GRUModel(nn.Module):
    def __init__(self, input_size=5, hidden_size=32, num_layers=2, output_size=1, dropout=0.0):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True,
                          dropout=dropout if num_layers > 1 else 0.0)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # GRU'da hücre durumu yok, tek h0 yetiyor
        h0 = x.new_zeros(self.num_layers, x.size(0), self.hidden_size)

        out, _ = self.gru(x, h0)
        return self.fc(out[:, -1, :])
