# CrickSense -- LSTM Pipeline Test Report

## Dataset & Video Information
- **Category**: General
- **Video File**: `General1.mp4`
- **Landmark File**: `General1_landmarks.csv`
- **Total Frames**: 76
- **Valid Frames (Target Detected)**: 76
- **Lost Frames**: 0

## Input Representation
- **Body Joints**: 33 MediaPipe Landmarks
- **Coordinates per Joint**: 3 (X, Y, Z)
- **Features per Frame**: 99 (33 joints × 3 coordinates)
- **Conceptual Sequence Format**: `[Batch, Time, Features]`
- **Input Tensor Shape**: `[1, 76, 99]` (`[1, 76, 99]`)

## Lost Frames Handling Method
In `General1_landmarks.csv`, frame validity is indicated by `target_detected`. For `General1.mp4`, all 76 frames contained valid detections (`target_detected == 1`). If lost frames (`target_detected == 0`) occur in future datasets, lost frame feature vectors default to 0.0 or linear interpolation from adjacent valid frames, preserving sequence length without introducing unverified spatial artifacts.

## LSTM Model Architecture
- **Model Class**: `BowlingLSTM`
- **Input Size**: 99
- **Hidden Size**: 128
- **LSTM Layers**: 2
- **Dropout**: 0.2
- **Output Activation Layer**: `Linear(128, 2)`
- **Total Model Parameters**: 249,602

## Forward Pass Execution
- **Output Tensor Shape**: `[1, 2]` (`[1, 2]`)
- **Forward Pass Status**: `PASS`
- **Execution Time**: `108.83 ms`
- **Training Status**: `NOT TRAINED`
- **Model Accuracy**: `N/A -- MODEL NOT TRAINED`

## Dimension Explanations
1. **Input Tensor `[1, 76, 99]`**:
   - `1`: Batch dimension representing a single video sample.
   - `76`: Temporal dimension representing 76 sequential video frames.
   - `99`: Spatial feature dimension (33 3D body joints × 3 coordinates: X, Y, Z).
2. **Output Tensor `[1, 2]`**:
   - `1`: Batch dimension representing single video prediction.
   - `2`: Raw logits scores for binary bowling delivery classification.
