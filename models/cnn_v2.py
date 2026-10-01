"""CNN v2 acordada con Álvaro. Entrada N,3,256,256; salida N,1 (logits)."""
import torch
from torch import nn


class CNNV2(nn.Module):
    """Tres bloques propios, sin preentrenamiento, BatchNorm ni dropout."""

    def __init__(self):
        super().__init__()
        self.bloques = nn.ModuleList([
            nn.Sequential(
                nn.Conv2d(entrada, salida, kernel_size=3, stride=1, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=2, stride=2),
            )
            for entrada, salida in [(3, 8), (8, 16), (16, 32)]
        ])
        self.promedio = nn.AdaptiveAvgPool2d(1)
        self.salida = nn.Linear(32, 1)
        for capa in self.modules():
            if isinstance(capa, nn.Conv2d):
                nn.init.kaiming_normal_(capa.weight, mode='fan_in', nonlinearity='relu')
                nn.init.zeros_(capa.bias)
            elif isinstance(capa, nn.Linear):
                nn.init.xavier_uniform_(capa.weight, gain=1.0)
                nn.init.zeros_(capa.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim != 4 or tuple(x.shape[1:]) != (3, 256, 256):
            raise ValueError('Entrada esperada: (N, 3, 256, 256), PRE/EARLY/LATE.')
        for bloque in self.bloques:
            x = bloque(x)
        return self.salida(self.promedio(x).flatten(1))
