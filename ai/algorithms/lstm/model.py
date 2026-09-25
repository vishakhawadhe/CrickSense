"""
=============================================================================
CrickSense -- Long Short-Term Memory (LSTM) Model for Bowling Pose Sequences
=============================================================================
Goal:
    Implement a clean PyTorch LSTM model architecture to process temporal 
    sequences of 33 MediaPipe body pose landmarks (3D coordinates: X, Y, Z).

Input Tensor Shape:
    [Batch, Time, Features] -> [N, T, 99]
    where:
      - N: Batch size (e.g., 1 for single video inference)
      - T: Number of valid video frames in bowling sequence
      - 99: 33 MediaPipe body joints * 3 spatial coordinates (X, Y, Z)

Output Tensor Shape:
    [Batch, Num_Classes] -> [N, 2]
    where:
      - 2: Binary logits output placeholder for bowling delivery classification

Architecture Specifications:
    - Input Size        : 99 (33 joints * 3 coordinates)
    - Hidden Size       : 128
    - Number of Layers  : 2
    - Dropout           : 0.2 (between stacked LSTM layers)
    - Output FC Layer   : Linear(128 -> 2)
    - Activation        : Raw logits output (Linear output layer)

Author : CrickSense Team
Date   : 2026
=============================================================================
"""

import torch
import torch.nn as nn
from typing import Tuple, Dict, Any


class BowlingLSTM(nn.Module):
    """
    LSTM Neural Network for Bowling Delivery Pose Sequence Processing.
    
    Processes temporal sequence of MediaPipe landmark coordinate vectors [N, T, 99]
    and outputs sequence-level classification logits [N, num_classes].
    """
    def __init__(
        self,
        input_size: int = 99,
        hidden_size: int = 128,
        num_layers: int = 2,
        num_classes: int = 2,
        dropout: float = 0.2
    ):
        super(BowlingLSTM, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_classes = num_classes
        self.dropout_rate = dropout
        
        # Stacked LSTM Layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        
        # Linear Classification Layer (Transforms last hidden state to logits)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of LSTM model.
        
        Args:
            x (torch.Tensor): Input landmark tensor of shape [N, T, 99] or [T, 99]
            
        Returns:
            torch.Tensor: Logits output tensor of shape [N, num_classes]
        """
        # Ensure 3D tensor shape [Batch, Time, Features]
        if x.dim() == 2:
            x = x.unsqueeze(0)  # [1, T, 99]
            
        if x.dim() != 3:
            raise ValueError(f"Expected 3D input tensor [Batch, Time, Features], got shape {list(x.shape)}")
            
        batch_size, seq_len, features = x.shape
        if features != self.input_size:
            raise ValueError(f"Expected feature dimension of {self.input_size}, got {features}")
            
        # Pass sequence through LSTM layers
        # lstm_out shape: [batch_size, seq_len, hidden_size]
        # (h_n, c_n) shapes: [num_layers, batch_size, hidden_size]
        lstm_out, (h_n, c_n) = self.lstm(x)
        
        # Take hidden state from final LSTM layer at final time step (h_n[-1])
        last_hidden = h_n[-1]  # Shape: [batch_size, hidden_size]
        
        # Compute output logits
        logits = self.fc(last_hidden)  # Shape: [batch_size, num_classes]
        
        return logits

    def get_num_parameters(self) -> int:
        """Return total number of trainable parameters in the model."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def get_architecture_summary(self) -> Dict[str, Any]:
        """Return model architecture summary details."""
        return {
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "num_classes": self.num_classes,
            "dropout": self.dropout_rate,
            "num_parameters": self.get_num_parameters()
        }


def count_parameters(model: nn.Module) -> int:
    """Utility function to count trainable parameters of any PyTorch module."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
