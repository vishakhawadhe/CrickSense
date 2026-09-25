# Spatial-Temporal Graph Convolutional Network (ST-GCN) Test Module

This directory contains the **test-only** ST-GCN pipeline module for CrickSense.

> [!IMPORTANT]
> **ST-GCN pipeline test only — model is untrained and output is not a valid prediction.**

---

## File Structure

```
ai/algorithms/stgcn/
├── graph.py        # MediaPipe 33-joint skeleton graph & spatial partitioning matrix
├── model.py        # PyTorch ST-GCN architecture (ConvTemporalGraphical + STGCNBlock)
├── test_stgcn.py   # Test execution script for forward-pass pipeline validation
└── README.md       # Documentation
```

---

## MediaPipe 33-Joint Skeleton Graph

- **Nodes ($V$)**: 33 body landmarks (MediaPipe BlazePose scheme)
- **Edges**: 35 physical body connections (undirected edges from MediaPipe `POSE_CONNECTIONS`)
- **Spatial Partitioning ($K = 3$)**:
  1. **Partition 0**: Self-loops ($I$)
  2. **Partition 1**: Centripetal connections (closer to center of mass/hips)
  3. **Partition 2**: Centrifugal connections (farther from center of mass/hips)
- **Adjacency Matrix ($A$)**: Shape $(3, 33, 33)$

---

## Input / Output Tensor Specification

- **Input Tensor Shape**: $(N, C, T, V) = (1, 3, 80, 33)$
  - $N = 1$: Batch size
  - $C = 3$: Channels (`x`, `y`, `z`)
  - $T = 80$: Frames in sequence
  - $V = 33$: Body joints
- **Output Tensor Shape**: $(N, \text{num\_classes}) = (1, 2)$

---

## How to Run

Execute the pipeline test using:

```bash
python ai/algorithms/stgcn/test_stgcn.py
```
