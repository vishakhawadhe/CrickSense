"""
=============================================================================
CrickSense -- ST-GCN Pipeline Test Script
=============================================================================
Goal:
    Perform a TEST-ONLY pipeline validation of Spatial-Temporal Graph
    Convolutional Network (ST-GCN) using one already-processed bowling video
    landmark CSV file.

Input:
    ai/data/landmarks/U19/Screen_Recording_20260919_111311_Instagram_1_landmarks.csv

Requirements Checked:
    1. CSV loaded successfully.
    2. 33 MediaPipe joints correctly parsed into (T, V, C) sequence format.
    3. MediaPipe 33-joint skeleton graph constructed.
    4. Adjacency matrix (K, V, V) constructed via spatial partitioning.
    5. ST-GCN input tensor created with shape (N, C, T, V).
    6. One forward pass executed without errors.

Disclaimer:
    ST-GCN pipeline test only — model is untrained and output is not a valid prediction.

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
from typing import Tuple, Dict, Optional, List

# Add project root directory to python path for relative imports if needed
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.stgcn.graph import MediaPipeGraph, JOINT_NAMES, MEDIAPIPE_CONNECTIONS
from algorithms.stgcn.model import STGCNModel


def load_landmark_csv(csv_path: str, channels: int = 3) -> Tuple[np.ndarray, int, int]:
    """
    Load skeleton landmarks from CSV file.
    CSV format expected:
      - video_id, frame_id, target_detected, landmark_0_x, landmark_0_y, landmark_0_z, landmark_0_visibility, ...

    Returns:
      data_tensor: numpy array of shape (C, T, V)
      num_frames: integer T
      num_joints: integer V (33)
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Landmark CSV file not found: {csv_path}")

    frames_data = []

    with open(csv_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("CSV file is empty.")

        for row_idx, row in enumerate(reader, start=1):
            if not row:
                continue
            
            video_id, frame_id, target_detected = row[0], int(row[1]), int(row[2])
            raw_landmarks = row[3:]

            # 33 joints, 4 attributes each (x, y, z, visibility)
            if len(raw_landmarks) != 33 * 4:
                raise ValueError(f"Row {row_idx}: Expected 132 landmark values, got {len(raw_landmarks)}")

            joint_coords = []
            for j in range(33):
                base_idx = j * 4
                if target_detected == 1:
                    x = float(raw_landmarks[base_idx])
                    y = float(raw_landmarks[base_idx + 1])
                    z = float(raw_landmarks[base_idx + 2])
                    vis = float(raw_landmarks[base_idx + 3]) if raw_landmarks[base_idx + 3] != '' else 0.0
                else:
                    # Target lost (0.0 fallback for forward pass shape test)
                    x, y, z, vis = 0.0, 0.0, 0.0, 0.0

                if channels == 3:
                    joint_coords.append([x, y, z])
                else:
                    joint_coords.append([x, y, z, vis])

            frames_data.append(joint_coords)  # Shape: (V, C)

    # Convert to numpy array of shape (T, V, C)
    data_np = np.array(frames_data, dtype=np.float32)
    num_frames, num_joints, num_channels = data_np.shape

    # Permute to (C, T, V) as required by ST-GCN
    data_tensor = np.transpose(data_np, (2, 0, 1))  # (C, T, V)

    return data_tensor, num_frames, num_joints


def run_stgcn_pipeline_test(csv_path: str):
    """Execute complete ST-GCN pipeline forward-pass test."""
    print("\n" + "=" * 80)
    print("  CrickSense -- Spatial-Temporal Graph Convolutional Network (ST-GCN)")
    print("  Pipeline Test-Only Execution")
    print("=" * 80 + "\n")

    test_passed = True
    error_message = None

    start_time = time.perf_counter()

    try:
        # Step 1: Load landmark CSV
        print(f"[STEP 1] Loading landmark CSV: {csv_path}")
        channels = 3  # (x, y, z)
        data_c_t_v, num_frames, num_joints = load_landmark_csv(csv_path, channels=channels)
        print(f"        Loaded {num_frames} frames, {num_joints} joints, {channels} coordinate channels (x, y, z).")

        # Step 2: Convert sequence to ST-GCN PyTorch Tensor format [N, C, T, V]
        print("\n[STEP 2] Formatting ST-GCN input tensor...")
        # Add batch dimension N = 1
        tensor_data = torch.from_numpy(data_c_t_v).unsqueeze(0)  # Shape: (1, C, T, V)
        input_shape = tensor_data.shape
        print(f"        ST-GCN Input Tensor Shape (N, C, T, V): {input_shape}")

        # Step 3: Construct MediaPipe 33-joint skeleton graph
        print("\n[STEP 3] Constructing MediaPipe 33-joint skeleton graph...")
        graph = MediaPipeGraph(strategy="spatial")
        node_count = graph.num_node
        edge_count = graph.num_edges
        adj_shape = graph.A.shape
        print(f"        Graph Node Count          : {node_count}")
        print(f"        Graph Edge Count          : {edge_count} physical body connections")
        print(f"        Adjacency Matrix Shape A  : {adj_shape} (Spatial partitioning: self, inward, outward)")

        # Step 4: Initialize ST-GCN Model
        print("\n[STEP 4] Initializing ST-GCN model architecture...")
        num_classes = 2  # Binary bowling delivery check placeholder
        model = STGCNModel(
            in_channels=channels,
            num_classes=num_classes,
            graph_adjacency=graph.A
        )
        model.eval()  # Evaluation mode for forward pass

        # Step 5: Perform single forward pass
        print("\n[STEP 5] Running single forward pass through ST-GCN model...")
        fp_start = time.perf_counter()
        with torch.no_grad():
            output_tensor = model(tensor_data)
        fp_end = time.perf_counter()

        execution_time_ms = (fp_end - fp_start) * 1000.0
        output_shape = output_tensor.shape
        forward_pass_success = True

    except Exception as e:
        forward_pass_success = False
        test_passed = False
        error_message = str(e)
        execution_time_ms = 0.0
        output_shape = None
        input_shape = None
        adj_shape = None
        node_count = 0
        edge_count = 0
        num_frames = 0
        num_joints = 0
        channels = 0

    total_time_ms = (time.perf_counter() - start_time) * 1000.0

    # Print Summary Report
    print("\n" + "=" * 80)
    print("  ST-GCN PIPELINE TEST RESULTS REPORT")
    print("=" * 80)
    print(f"  Input CSV                     : {csv_path}")
    print(f"  Number of Frames (T)          : {num_frames}")
    print(f"  Number of Joints (V)          : {num_joints}")
    print(f"  Number of Channels (C)        : {channels}")
    print(f"  Graph Node Count              : {node_count}")
    print(f"  Graph Edge Count              : {edge_count}")
    print(f"  Adjacency Matrix Shape        : {adj_shape}")
    print(f"  ST-GCN Input Tensor Shape     : {input_shape}")
    print(f"  Model Output Tensor Shape     : {output_shape}")
    print(f"  Forward Pass Completed        : {forward_pass_success}")
    print(f"  Forward Pass Execution Time   : {execution_time_ms:.2f} ms")
    print("=" * 80)

    # Mandatory Disclaimer
    print("\n  ST-GCN pipeline test only — model is untrained and output is not a valid prediction.\n")

    # Final Verdict
    if test_passed:
        print("  TEST RESULT: PASS")
    else:
        print(f"  TEST RESULT: FAIL ({error_message})")
    print("=" * 80 + "\n")

    return test_passed


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        PROJECT_ROOT, "data", "landmarks", "U19", "Screen_Recording_20260919_111311_Instagram_1_landmarks.csv"
    )
    success = run_stgcn_pipeline_test(csv_file)
    sys.exit(0 if success else 1)
