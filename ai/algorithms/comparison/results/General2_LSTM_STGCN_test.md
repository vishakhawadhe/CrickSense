# CrickSense -- General2 Dataset Test Report (LSTM & ST-GCN)

This report presents separate single-video pipeline test evaluations for **LSTM** and **ST-GCN** architectures on `General2.mp4` landmark data.

> [!NOTE]
> Models are evaluated strictly in test-only mode. No model training, hyperparameter tuning, accuracy evaluation, or inter-model comparison has been conducted.

---

## LSTM -- General2

- **Input**: `General2.mp4` / `General2_landmarks.csv`
- **Frames (Total)**: 177
- **Valid Frames**: 170 (Lost frames: 7)
- **Input Tensor Shape**: `[1, 177, 99]` (`[Batch=1, Time=177, Features=99]`)
- **Output Tensor Shape**: `[1, 2]` (`[Batch=1, Num_Classes=2]`)
- **Forward Pass**: `PASS`
- **Inference Time**: `138.60 ms`
- **Model Status**: `NOT TRAINED`
- **Prediction Status**: `N/A -- MODEL NOT TRAINED`

---

## ST-GCN -- General2

- **Input**: `General2.mp4` / `General2_landmarks.csv`
- **Frames (Total)**: 177
- **Valid Frames**: 170 (Lost frames: 7)
- **Input Tensor Shape**: `[1, 3, 177, 33]` (`[Batch=1, Channels=3, Time=177, Vertices=33]`)
- **Output Tensor Shape**: `[1, 2]` (`[Batch=1, Num_Classes=2]`)
- **Forward Pass**: `PASS`
- **Inference Time**: `169.55 ms`
- **Model Status**: `NOT TRAINED`
- **Prediction Status**: `N/A -- MODEL NOT TRAINED`
