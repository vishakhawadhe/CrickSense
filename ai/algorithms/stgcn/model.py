"""
=============================================================================
Spatial-Temporal Graph Convolutional Network (ST-GCN) - PyTorch Implementation
=============================================================================
Reference:
    Yan et al., "Spatial Temporal Graph Convolutional Networks for Skeleton-Based
    Action Recognition", AAAI 2018.

This module provides a clean PyTorch ST-GCN architecture for skeleton sequence
processing.

Input Tensor Shape : (N, C, T, V)
  - N: Batch size (e.g. 1)
  - C: Number of joint channels (x, y, z or x, y, z, visibility)
  - T: Sequence frames (e.g. 80)
  - V: Skeleton joints (33 for MediaPipe)

Author : CrickSense Team
Date   : 2026
=============================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple


class ConvTemporalGraphical(nn.Module):
    """
    Spatial Graph Convolution layer.
    Computes spatial graph convolutions on node features given adjacency matrix A (K, V, V).
    """

    def __init__(self, in_channels: int, out_channels: int, K: int = 3) -> None:
        super().__init__()
        self.K = K
        self.conv = nn.Conv2d(
            in_channels=in_channels,
            out_channels=out_channels * K,
            kernel_size=(1, 1),
            padding=(0, 0),
            stride=(1, 1),
            bias=True
        )

    def forward(self, x: torch.Tensor, A: torch.Tensor) -> torch.Tensor:
        """
        x: (N, C_in, T, V)
        A: (K, V, V)
        Returns: (N, C_out, T, V)
        """
        N, C, T, V = x.size()
        x_conv = self.conv(x)  # (N, K * C_out, T, V)
        x_conv = x_conv.view(N, self.K, -1, T, V)  # (N, K, C_out, T, V)

        # Einstein summation over spatial dimension V using Adjacency A
        # n: batch, k: partition, c: channels, t: frames, v: source joint, w: target joint
        out = torch.einsum('nkctv, kvw -> nctw', x_conv, A)
        return out.contiguous()


class STGCNBlock(nn.Module):
    """
    Spatial-Temporal Graph Convolutional Block.
    Applies spatial graph convolution followed by 1D temporal convolution.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        A: torch.Tensor,
        stride: int = 1,
        dropout: float = 0.0,
        temporal_kernel_size: int = 9
    ) -> None:
        super().__init__()

        # Register adjacency matrix as buffer
        self.register_buffer('A', A)
        K = A.size(0)

        # Spatial Graph Convolution
        self.gcn = ConvTemporalGraphical(in_channels, out_channels, K=K)
        self.bn_gcn = nn.BatchNorm2d(out_channels)

        # Temporal Convolution (conv along T dimension)
        padding = (temporal_kernel_size - 1) // 2
        self.tcn = nn.Sequential(
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size=(temporal_kernel_size, 1),
                stride=(stride, 1),
                padding=(padding, 0)
            ),
            nn.BatchNorm2d(out_channels),
            nn.Dropout(dropout, inplace=True)
        )

        # Residual Connection
        if (in_channels != out_channels) or (stride != 1):
            self.residual = nn.Sequential(
                nn.Conv2d(
                    in_channels,
                    out_channels,
                    kernel_size=(1, 1),
                    stride=(stride, 1)
                ),
                nn.BatchNorm2d(out_channels)
            )
        else:
            self.residual = nn.Identity()

        self.relu = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (N, C_in, T, V)
        Returns: (N, C_out, T_out, V)
        """
        res = self.residual(x)

        # Spatial GCN
        x_gcn = self.gcn(x, self.A)
        x_gcn = self.bn_gcn(x_gcn)
        x_gcn = self.relu(x_gcn)

        # Temporal Conv
        x_stgcn = self.tcn(x_gcn)

        # Residual Addition
        out = self.relu(x_stgcn + res)
        return out


class STGCNModel(nn.Module):
    """
    Complete ST-GCN Model for forward pass execution checks.
    Stack of 3 ST-GCN blocks with Global Average Pooling & Linear Output.
    """

    def __init__(
        self,
        in_channels: int,
        num_classes: int,
        graph_adjacency: np.ndarray,
        edge_importance_weighting: bool = True
    ) -> None:
        super().__init__()

        # Convert Adjacency matrix (K, V, V) to PyTorch tensor float32
        A_tensor = torch.from_numpy(graph_adjacency).float()
        self.num_node = A_tensor.size(1)
        self.num_partition = A_tensor.size(0)

        # Data batch norm for input channel normalization
        self.data_bn = nn.BatchNorm1d(in_channels * self.num_node)

        # ST-GCN Blocks
        self.st_gcn_1 = STGCNBlock(in_channels, 64, A_tensor, stride=1)
        self.st_gcn_2 = STGCNBlock(64, 128, A_tensor, stride=1)
        self.st_gcn_3 = STGCNBlock(128, 256, A_tensor, stride=1)

        # Final Classification FC Layer
        self.fc = nn.Linear(256, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (N, C, T, V)
        Returns: (N, num_classes)
        """
        N, C, T, V = x.size()

        # Batch Normalization across channels & joints
        x_bn = x.permute(0, 1, 3, 2).contiguous().view(N, C * V, T)
        x_bn = self.data_bn(x_bn)
        x_bn = x_bn.view(N, C, V, T).permute(0, 1, 3, 2).contiguous()  # (N, C, T, V)

        # Forward pass through ST-GCN layers
        x1 = self.st_gcn_1(x_bn)  # (N, 64, T, V)
        x2 = self.st_gcn_2(x1)    # (N, 128, T, V)
        x3 = self.st_gcn_3(x2)    # (N, 256, T, V)

        # Global Average Pooling over time T and space V
        x_pool = x3.mean(dim=[-2, -1])  # (N, 256)

        # Linear projection
        out = self.fc(x_pool)  # (N, num_classes)
        return out
