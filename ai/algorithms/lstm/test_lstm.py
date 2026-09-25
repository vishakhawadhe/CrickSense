"""
=============================================================================
CrickSense -- LSTM Pipeline Test & Report Generation Script
=============================================================================
Goal:
    Perform a complete forward-pass validation of the Long Short-Term Memory 
    (LSTM) architecture on the General-category bowling video (General1.mp4).

Inputs:
    - ai/data/raw/General/General1.mp4
    - ai/data/landmarks/General/General1_landmarks.csv

Outputs Generated:
    - ai/output/lstm_general/General1_lstm_demo.mp4
    - ai/algorithms/lstm/results/general1_lstm_test.csv
    - ai/algorithms/lstm/results/general1_lstm_test.md

Requirements:
    1. Reads actual number of frames (T) from General1_landmarks.csv.
    2. Formats tensor into [Batch=1, Time=T, Features=99].
    3. Runs PyTorch LSTM forward pass.
    4. Measures execution time in milliseconds.
    5. Saves CSV and Markdown reports.
    6. Generates MP4 demonstration video.
    7. Prints standardized terminal output summary.

Author : CrickSense Team
Date   : 2026
=============================================================================
"""

import os
import sys
import csv
import time
import torch
import numpy as np
from typing import Tuple, Dict, Any

# Add project root directory to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.lstm.model import BowlingLSTM, count_parameters
from algorithms.lstm.generate_lstm_demo import load_lstm_landmark_csv, generate_lstm_demo_video


def run_lstm_analysis():
    """Main execution function for LSTM Analysis on General1 video."""
    csv_relative_path = os.path.join("ai", "data", "landmarks", "General", "General1_landmarks.csv")
    csv_path = os.path.join(PROJECT_ROOT, "data", "landmarks", "General", "General1_landmarks.csv")
    video_path = os.path.join(PROJECT_ROOT, "data", "raw", "General", "General1.mp4")
    
    results_dir = os.path.join(PROJECT_ROOT, "algorithms", "lstm", "results")
    output_dir = os.path.join(PROJECT_ROOT, "output", "lstm_general")
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    test_csv_path = os.path.join(results_dir, "general1_lstm_test.csv")
    test_md_path = os.path.join(results_dir, "general1_lstm_test.md")
    video_output_path = os.path.join(output_dir, "General1_lstm_demo.mp4")

    # Step 1: Load landmarks and format input tensor
    data_t_99, total_frames, valid_frames, lost_frames = load_lstm_landmark_csv(csv_path)
    
    # Input Tensor Shape [Batch, Time, Features] -> [1, T, 99]
    input_tensor = torch.from_numpy(data_t_99).unsqueeze(0)  # Shape: [1, T, 99]
    T = input_tensor.shape[1]
    num_joints = 33
    features_per_frame = 99

    # Step 2: Initialize LSTM Model
    input_size = 99
    hidden_size = 128
    num_layers = 2
    num_classes = 2

    model = BowlingLSTM(
        input_size=input_size,
        hidden_size=hidden_size,
        num_layers=num_layers,
        num_classes=num_classes,
        dropout=0.2
    )
    model.eval()
    total_params = model.get_num_parameters()

    # Step 3: Execute Forward Pass and Measure Execution Time
    forward_pass_status = "FAIL"
    execution_time_ms = 0.0

    try:
        fp_start = time.perf_counter()
        with torch.no_grad():
            output_tensor = model(input_tensor)
        fp_end = time.perf_counter()
        
        execution_time_ms = (fp_end - fp_start) * 1000.0
        forward_pass_status = "PASS"
    except Exception as e:
        output_tensor = torch.empty(0)
        forward_pass_status = f"FAIL ({str(e)})"

    # Step 4: Write CSV Report
    with open(test_csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerow(["dataset", "General"])
        writer.writerow(["video", "General1.mp4"])
        writer.writerow(["total_frames", total_frames])
        writer.writerow(["valid_frames", valid_frames])
        writer.writerow(["lost_frames", lost_frames])
        writer.writerow(["num_joints", num_joints])
        writer.writerow(["coordinates", "X/Y/Z"])
        writer.writerow(["features_per_frame", features_per_frame])
        writer.writerow(["input_tensor_shape", str(list(input_tensor.shape))])
        writer.writerow(["lstm_hidden_size", hidden_size])
        writer.writerow(["lstm_num_layers", num_layers])
        writer.writerow(["output_tensor_shape", str(list(output_tensor.shape))])
        writer.writerow(["num_model_parameters", total_params])
        writer.writerow(["forward_pass_execution_time_ms", f"{execution_time_ms:.2f}"])
        writer.writerow(["forward_pass", forward_pass_status])
        writer.writerow(["training_status", "NOT TRAINED"])
        writer.writerow(["accuracy", "N/A -- MODEL NOT TRAINED"])

    # Step 5: Write Markdown Report
    md_content = f"""# CrickSense -- LSTM Pipeline Test Report

## Dataset & Video Information
- **Category**: General
- **Video File**: `General1.mp4`
- **Landmark File**: `General1_landmarks.csv`
- **Total Frames**: {total_frames}
- **Valid Frames (Target Detected)**: {valid_frames}
- **Lost Frames**: {lost_frames}

## Input Representation
- **Body Joints**: 33 MediaPipe Landmarks
- **Coordinates per Joint**: 3 (X, Y, Z)
- **Features per Frame**: 99 (33 joints × 3 coordinates)
- **Conceptual Sequence Format**: `[Batch, Time, Features]`
- **Input Tensor Shape**: `{list(input_tensor.shape)}` (`[1, {T}, 99]`)

## Lost Frames Handling Method
In `General1_landmarks.csv`, frame validity is indicated by `target_detected`. For `General1.mp4`, all {valid_frames} frames contained valid detections (`target_detected == 1`). If lost frames (`target_detected == 0`) occur in future datasets, lost frame feature vectors default to 0.0 or linear interpolation from adjacent valid frames, preserving sequence length without introducing unverified spatial artifacts.

## LSTM Model Architecture
- **Model Class**: `BowlingLSTM`
- **Input Size**: {input_size}
- **Hidden Size**: {hidden_size}
- **LSTM Layers**: {num_layers}
- **Dropout**: 0.2
- **Output Activation Layer**: `Linear({hidden_size}, {num_classes})`
- **Total Model Parameters**: {total_params:,}

## Forward Pass Execution
- **Output Tensor Shape**: `{list(output_tensor.shape)}` (`[1, {num_classes}]`)
- **Forward Pass Status**: `{forward_pass_status}`
- **Execution Time**: `{execution_time_ms:.2f} ms`
- **Training Status**: `NOT TRAINED`
- **Model Accuracy**: `N/A -- MODEL NOT TRAINED`

## Dimension Explanations
1. **Input Tensor `[1, {T}, 99]`**:
   - `1`: Batch dimension representing a single video sample.
   - `{T}`: Temporal dimension representing {T} sequential video frames.
   - `99`: Spatial feature dimension (33 3D body joints × 3 coordinates: X, Y, Z).
2. **Output Tensor `[1, {num_classes}]`**:
   - `1`: Batch dimension representing single video prediction.
   - `{num_classes}`: Raw logits scores for binary bowling delivery classification.
"""
    with open(test_md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    # Step 6: Generate MP4 Demonstration Video
    video_path_gen = generate_lstm_demo_video()

    # Step 7: Print Standardized Final Terminal Output
    print("\n========================================")
    print("CRICKSENSE LSTM ANALYSIS")
    print("========================================\n")
    print("Category:")
    print("GENERAL\n")
    print("Video:")
    print("General1.mp4\n")
    print("Frames:")
    print(f"{total_frames}\n")
    print("Joints:")
    print(f"{num_joints}\n")
    print("Features:")
    print(f"{features_per_frame}\n")
    print("Input Tensor:")
    print(f"{input_tensor.shape}\n")
    print("Output Tensor:")
    print(f"{output_tensor.shape}\n")
    print("LSTM Parameters:")
    print(f"{total_params}\n")
    print("Forward Pass:")
    print(f"{forward_pass_status}\n")
    print("Execution Time:")
    print(f"{execution_time_ms:.2f} ms\n")
    print("Training Status:")
    print("NOT TRAINED\n")
    print("Accuracy:")
    print("N/A -- MODEL NOT TRAINED\n")
    print("Video Output:")
    print(f"{video_output_path}\n")
    print("Report:")
    print(f"{test_md_path}\n")
    print("========================================\n")


if __name__ == "__main__":
    run_lstm_analysis()
