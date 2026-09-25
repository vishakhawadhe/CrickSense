# CrickSense -- Long Short-Term Memory (LSTM) Analysis Module

## Overview
This directory contains the **Long Short-Term Memory (LSTM)** analysis module for the CrickSense project. The module processes temporal pose landmark sequences extracted from cricket bowling videos to model dynamic temporal dependencies across frames.

---

## Model Architecture Specifications (`ai/algorithms/lstm/model.py`)

The LSTM architecture is designed specifically for temporal sequence processing of 33-joint MediaPipe body pose coordinates.

| Specification Parameter | Value / Detail |
| :--- | :--- |
| **Model Class** | `BowlingLSTM` |
| **Input Feature Dimension** | `99` (33 body joints × 3 spatial coordinates: X, Y, Z) |
| **Hidden State Dimension** | `128` |
| **Number of Stacked LSTM Layers** | `2` |
| **Layer Dropout** | `0.2` (applied between stacked LSTM layers) |
| **Output Dimension** | `2` (binary logits output placeholder) |
| **Activation / Output Layer** | Unactivated Linear Fully-Connected Layer `nn.Linear(128, 2)` |
| **Total Trainable Parameters** | `249,602` |

### Parameter Count Breakdown
- **LSTM Layer 1**: $4 \times 128 \times (99 + 128 + 2) = 117,248$
- **LSTM Layer 2**: $4 \times 128 \times (128 + 128 + 2) = 132,096$
- **Linear FC Layer**: $128 \times 2 + 2 = 258$
- **Total Parameters**: $117,248 + 132,096 + 258 = 249,602$

---

## Input Representation & Tensor Dimensions

### 1. Spatial Representation (99 Features per Frame)
Each video frame is represented by 33 MediaPipe body joints:
- Landmark 0 through Landmark 32.
- For each landmark, three spatial coordinates are extracted:
  - $X$: Normalized horizontal coordinate $[0.0, 1.0]$
  - $Y$: Normalized vertical coordinate $[0.0, 1.0]$
  - $Z$: Depth coordinate relative to hip midpoint
- Total features per frame: $33 \times 3 = 99$.

### 2. Temporal Representation & Tensor Formatting
The full bowling sequence is formatted as a 3D PyTorch tensor:
```
[Batch, Time, Features]  -->  [1, T, 99]
```
For `General1.mp4`:
- `Batch = 1`: Single video sequence sample.
- `Time = 76`: Actual frame count extracted directly from `General1_landmarks.csv`.
- `Features = 99`: 33 joints × 3 coordinates per frame.

---

## Lost Frame Handling Strategy

Landmark quality audit tracks target bowler presence via `target_detected` (1 for detected, 0 for lost).
- **Current General1 Video**: All 76 frames contain valid detections (`target_detected == 1`).
- **Lost Frame Handling Policy**: When `target_detected == 0`, lost landmark values default to 0.0 or linear interpolation from surrounding valid frames. This guarantees contiguous sequence lengths without inventing artificial spatial trajectories.

---

## Execution & Verification Scripts

### 1. Run Pipeline Forward Pass & Generate Reports
```bash
python ai/algorithms/lstm/test_lstm.py
```
This executes:
1. Parsing of landmark CSV without modifying original CSV files.
2. Tensor formatting (`[1, 76, 99]`).
3. Model forward pass execution.
4. Generation of CSV and Markdown reports in `ai/algorithms/lstm/results/`.
5. Generation of MP4 visualization video in `ai/output/lstm_general/General1_lstm_demo.mp4`.
6. Standardized final terminal summary printout.

### 2. Generate Demonstration MP4 Standalone
```bash
python ai/algorithms/lstm/generate_lstm_demo.py
```

---

## Training Status & Future ST-GCN Benchmarking

> [!IMPORTANT]
> - **Current Model Status**: `NOT TRAINED`. Output logits represent uninitialized model forward-pass verification.
> - **Predictions & Accuracy**: Reported strictly as `N/A -- MODEL NOT TRAINED`.
> - **Future ST-GCN Comparison**: The data processing interface (`[1, T, 99]`) is modularly standard to enable future direct comparisons with ST-GCN (`[1, 3, T, 33]`) on identical datasets and train/test splits.
