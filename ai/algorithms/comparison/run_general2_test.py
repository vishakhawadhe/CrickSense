"""
=============================================================================
CrickSense -- General2 LSTM & ST-GCN Test Execution & Report Runner
=============================================================================
Goal:
    Execute both LSTM and ST-GCN model pipelines on General2.mp4 landmark sequence.
    Generate separate demonstration videos and a combined results markdown report.

Inputs:
    ai/data/raw/General/General2.mp4
    ai/data/landmarks/General/General2_landmarks.csv

Outputs:
    ai/output/lstm_general/General2_lstm_demo.mp4
    ai/output/stgcn_general/General2_stgcn_demo.mp4
    ai/algorithms/comparison/results/General2_LSTM_STGCN_test.md

Requirements Checked:
    - Runs LSTM pipeline on General2 (Shape: [1, T, 99])
    - Runs ST-GCN pipeline on General2 (Shape: [1, 3, T, 33])
    - Does NOT modify existing model architectures or graphs
    - Does NOT perform model comparison or calculate accuracy
    - Clearly marks model status as NOT TRAINED and prediction as N/A
    - Prints formatted terminal summary report

Author : CrickSense Team
Date   : 2026
=============================================================================
"""

import os
import sys
import time
import torch
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.lstm.model import BowlingLSTM
from algorithms.lstm.generate_lstm_demo import load_lstm_landmark_csv
from algorithms.stgcn.graph import MediaPipeGraph
from algorithms.stgcn.model import STGCNModel
from algorithms.stgcn.test_stgcn import load_landmark_csv as load_stgcn_landmark_csv
from algorithms.comparison.generate_general2_videos import render_general2_demo_video


def run_general2_tests():
    """Execute pipeline tests for LSTM and ST-GCN on General2."""
    csv_path = os.path.join(PROJECT_ROOT, "data", "landmarks", "General", "General2_landmarks.csv")
    video_path = os.path.join(PROJECT_ROOT, "data", "raw", "General", "General2.mp4")

    results_dir = os.path.join(PROJECT_ROOT, "algorithms", "comparison", "results")
    os.makedirs(results_dir, exist_ok=True)
    report_md_path = os.path.join(results_dir, "General2_LSTM_STGCN_test.md")

    print("\n" + "=" * 80)
    print("  CrickSense -- General2 LSTM & ST-GCN Pipeline Tests")
    print("=" * 80 + "\n")

    # -------------------------------------------------------------------------
    # 1. LSTM Pipeline Test on General2
    # -------------------------------------------------------------------------
    print("[1/3] Running LSTM pipeline test on General2...")
    lstm_data_t_99, lstm_total_frames, lstm_valid_frames, lstm_lost_frames = load_lstm_landmark_csv(csv_path)
    lstm_input_tensor = torch.from_numpy(lstm_data_t_99).unsqueeze(0)  # Shape: [1, T, 99]

    lstm_model = BowlingLSTM(input_size=99, hidden_size=128, num_layers=2, num_classes=2)
    lstm_model.eval()

    lstm_fp_status = "FAIL"
    lstm_exec_time_ms = 0.0

    try:
        t0 = time.perf_counter()
        with torch.no_grad():
            lstm_output_tensor = lstm_model(lstm_input_tensor)
        t1 = time.perf_counter()
        lstm_exec_time_ms = (t1 - t0) * 1000.0
        lstm_fp_status = "PASS"
    except Exception as e:
        lstm_output_tensor = torch.empty(0)
        lstm_fp_status = f"FAIL ({str(e)})"

    lstm_input_shape_str = f"{list(lstm_input_tensor.shape)}"
    lstm_output_shape_str = f"{list(lstm_output_tensor.shape)}"

    print(f"      Input Tensor Shape  : {lstm_input_tensor.shape}")
    print(f"      Output Tensor Shape : {lstm_output_tensor.shape}")
    print(f"      Forward Pass        : {lstm_fp_status}")
    print(f"      Inference Time      : {lstm_exec_time_ms:.2f} ms\n")

    # -------------------------------------------------------------------------
    # 2. ST-GCN Pipeline Test on General2
    # -------------------------------------------------------------------------
    print("[2/3] Running ST-GCN pipeline test on General2...")
    stgcn_data_c_t_v, stgcn_total_frames, stgcn_num_joints = load_stgcn_landmark_csv(csv_path, channels=3)
    stgcn_input_tensor = torch.from_numpy(stgcn_data_c_t_v).unsqueeze(0)  # Shape: [1, 3, T, 33]

    stgcn_graph = MediaPipeGraph(strategy="spatial")
    stgcn_model = STGCNModel(in_channels=3, num_classes=2, graph_adjacency=stgcn_graph.A)
    stgcn_model.eval()

    stgcn_fp_status = "FAIL"
    stgcn_exec_time_ms = 0.0

    try:
        t0 = time.perf_counter()
        with torch.no_grad():
            stgcn_output_tensor = stgcn_model(stgcn_input_tensor)
        t1 = time.perf_counter()
        stgcn_exec_time_ms = (t1 - t0) * 1000.0
        stgcn_fp_status = "PASS"
    except Exception as e:
        stgcn_output_tensor = torch.empty(0)
        stgcn_fp_status = f"FAIL ({str(e)})"

    stgcn_input_shape_str = f"{list(stgcn_input_tensor.shape)}"
    stgcn_output_shape_str = f"{list(stgcn_output_tensor.shape)}"

    print(f"      Input Tensor Shape  : {stgcn_input_tensor.shape}")
    print(f"      Output Tensor Shape : {stgcn_output_tensor.shape}")
    print(f"      Forward Pass        : {stgcn_fp_status}")
    print(f"      Inference Time      : {stgcn_exec_time_ms:.2f} ms\n")

    # -------------------------------------------------------------------------
    # 3. Generate Videos
    # -------------------------------------------------------------------------
    print("[3/3] Generating demonstration MP4 videos...")
    lstm_video_path = render_general2_demo_video("LSTM", lstm_input_shape_str, lstm_output_shape_str)
    stgcn_video_path = render_general2_demo_video("ST-GCN", stgcn_input_shape_str, stgcn_output_shape_str)

    # -------------------------------------------------------------------------
    # 4. Generate Combined Markdown Report
    # -------------------------------------------------------------------------
    report_md_content = f"""# CrickSense -- General2 Dataset Test Report (LSTM & ST-GCN)

This report presents separate single-video pipeline test evaluations for **LSTM** and **ST-GCN** architectures on `General2.mp4` landmark data.

> [!NOTE]
> Models are evaluated strictly in test-only mode. No model training, hyperparameter tuning, accuracy evaluation, or inter-model comparison has been conducted.

---

## LSTM -- General2

- **Input**: `General2.mp4` / `General2_landmarks.csv`
- **Frames (Total)**: {lstm_total_frames}
- **Valid Frames**: {lstm_valid_frames} (Lost frames: {lstm_lost_frames})
- **Input Tensor Shape**: `{list(lstm_input_tensor.shape)}` (`[Batch=1, Time={lstm_total_frames}, Features=99]`)
- **Output Tensor Shape**: `{list(lstm_output_tensor.shape)}` (`[Batch=1, Num_Classes=2]`)
- **Forward Pass**: `{lstm_fp_status}`
- **Inference Time**: `{lstm_exec_time_ms:.2f} ms`
- **Model Status**: `NOT TRAINED`
- **Prediction Status**: `N/A -- MODEL NOT TRAINED`

---

## ST-GCN -- General2

- **Input**: `General2.mp4` / `General2_landmarks.csv`
- **Frames (Total)**: {stgcn_total_frames}
- **Valid Frames**: {lstm_valid_frames} (Lost frames: {lstm_lost_frames})
- **Input Tensor Shape**: `{list(stgcn_input_tensor.shape)}` (`[Batch=1, Channels=3, Time={stgcn_total_frames}, Vertices=33]`)
- **Output Tensor Shape**: `{list(stgcn_output_tensor.shape)}` (`[Batch=1, Num_Classes=2]`)
- **Forward Pass**: `{stgcn_fp_status}`
- **Inference Time**: `{stgcn_exec_time_ms:.2f} ms`
- **Model Status**: `NOT TRAINED`
- **Prediction Status**: `N/A -- MODEL NOT TRAINED`
"""

    with open(report_md_path, 'w', encoding='utf-8') as f:
        f.write(report_md_content)

    # -------------------------------------------------------------------------
    # 5. Final Terminal Output
    # -------------------------------------------------------------------------
    print("====================================")
    print("GENERAL2 LSTM TEST")
    print("====================================\n")
    print("Input:")
    print("General2.mp4\n")
    print("Input tensor:")
    print(f"{lstm_input_tensor.shape}\n")
    print("Output tensor:")
    print(f"{lstm_output_tensor.shape}\n")
    print("Forward pass:")
    print(f"{lstm_fp_status}\n")
    print("Status:")
    print("NOT TRAINED\n")
    print("====================================")
    print("GENERAL2 ST-GCN TEST")
    print("====================================\n")
    print("Input:")
    print("General2.mp4\n")
    print("Input tensor:")
    print(f"{stgcn_input_tensor.shape}\n")
    print("Output tensor:")
    print(f"{stgcn_output_tensor.shape}\n")
    print("Forward pass:")
    print(f"{stgcn_fp_status}\n")
    print("Status:")
    print("NOT TRAINED\n")
    print("====================================\n")
    print(f"LSTM Video Output:   {lstm_video_path}")
    print(f"ST-GCN Video Output: {stgcn_video_path}")
    print(f"Markdown Report:     {report_md_path}\n")


if __name__ == "__main__":
    run_general2_tests()
