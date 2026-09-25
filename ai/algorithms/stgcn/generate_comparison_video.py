"""
=============================================================================
CrickSense -- LSTM vs ST-GCN Model Comparison Video Generator
=============================================================================
Goal:
    Generate a side-by-side visual comparison video MP4 displaying:
      1. Original bowling video feed with MediaPipe 33-joint skeleton & target bounding box
      2. Input metadata (Category: GENERAL, General1.mp4, Frame counter, Target status)
      3. LSTM Technical Pipeline (Input shape [1, 76, 99], Output shape [1, 2], Status: NOT TRAINED)
      4. ST-GCN Technical Pipeline (Input shape [1, 3, 76, 33], Output shape [1, 2], Forward Pass: PASS, Status: NOT TRAINED)
      5. CRICKSENSE ANALYSIS PANEL (Exact 7 N/A rows)
      6. Architecture Comparison Explanation (Temporal vs Spatial-Temporal Graph)

Input:
    ai/data/raw/General/General1.mp4
    ai/data/landmarks/General/General1_landmarks.csv

Output:
    ai/output/model_comparison/General1_LSTM_vs_STGCN.mp4

Author : CrickSense Team
Date   : 2026
=============================================================================
"""

import os
import sys
import csv
import cv2
import time
import torch
import torch.nn as nn
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.stgcn.graph import MediaPipeGraph, MEDIAPIPE_CONNECTIONS
from algorithms.stgcn.model import STGCNModel
from algorithms.stgcn.test_stgcn import load_landmark_csv


# Minimal PyTorch LSTM Model for pipeline shape resolution
class MinimalLSTMModel(nn.Module):
    def __init__(self, in_features=99, hidden_dim=128, num_classes=2):
        super().__init__()
        self.lstm = nn.LSTM(in_features, hidden_dim, num_layers=2, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


def generate_comparison_video():
    raw_video_path = os.path.join(PROJECT_ROOT, "data", "raw", "General", "General1.mp4")
    landmark_csv_path = os.path.join(PROJECT_ROOT, "data", "landmarks", "General", "General1_landmarks.csv")
    output_dir = os.path.join(PROJECT_ROOT, "output", "model_comparison")
    output_video_path = os.path.join(output_dir, "General1_LSTM_vs_STGCN.mp4")

    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 80)
    print("  CrickSense -- LSTM vs ST-GCN Visual Model Comparison Video Generator")
    print("=" * 80)
    print(f"  Input Video  : {raw_video_path}")
    print(f"  Landmark CSV : {landmark_csv_path}")
    print(f"  Output Video : {output_video_path}")
    print("=" * 80 + "\n")

    # 1. Load Landmarks & Resolve ST-GCN Shapes
    print("[1/4] Resolving ST-GCN pipeline shapes & forward pass...")
    data_c_t_v, T, V = load_landmark_csv(landmark_csv_path, channels=3)  # Shape: (3, T, 33)
    tensor_stgcn_input = torch.from_numpy(data_c_t_v).unsqueeze(0)  # Shape: (1, 3, T, 33)

    graph = MediaPipeGraph(strategy="spatial")
    stgcn_model = STGCNModel(in_channels=3, num_classes=2, graph_adjacency=graph.A)
    stgcn_model.eval()

    with torch.no_grad():
        out_stgcn = stgcn_model(tensor_stgcn_input)

    stgcn_in_shape_str = f"[{tensor_stgcn_input.shape[0]}, {tensor_stgcn_input.shape[1]}, {tensor_stgcn_input.shape[2]}, {tensor_stgcn_input.shape[3]}]"
    stgcn_out_shape_str = f"[{out_stgcn.shape[0]}, {out_stgcn.shape[1]}]"
    stgcn_status = "NOT TRAINED"
    stgcn_fp_status = "PASS"

    # 2. Resolve LSTM Shapes
    print("[2/4] Resolving LSTM pipeline shapes & forward pass...")
    # Reshape (3, T, 33) -> (N, T, V*C) = (1, T, 99)
    data_t_vc = np.transpose(data_c_t_v, (1, 2, 0)).reshape(1, T, V * 3)
    tensor_lstm_input = torch.from_numpy(data_t_vc).float()

    lstm_model = MinimalLSTMModel(in_features=99, hidden_dim=128, num_classes=2)
    lstm_model.eval()

    with torch.no_grad():
        out_lstm = lstm_model(tensor_lstm_input)

    lstm_in_shape_str = f"[{tensor_lstm_input.shape[0]}, {tensor_lstm_input.shape[1]}, {tensor_lstm_input.shape[2]}]"
    lstm_out_shape_str = f"[{out_lstm.shape[0]}, {out_lstm.shape[1]}]"
    lstm_status = "NOT TRAINED"

    # 3. Open Video File & CSV
    cap = cv2.VideoCapture(raw_video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {raw_video_path}")

    vid_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or np.isnan(fps):
        fps = 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    with open(landmark_csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
    csv_rows = reader[1:]

    # 4. Setup Video Writer
    panel_width = 720
    canvas_width = vid_width + panel_width
    canvas_height = vid_height

    print(f"      Canvas Resolution : {canvas_width} x {canvas_height} @ {fps:.2f} FPS")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_video_path, fourcc, fps, (canvas_width, canvas_height))

    if not writer.isOpened():
        raise RuntimeError(f"Could not create VideoWriter at: {output_video_path}")

    # Color Palette (BGR)
    COLOR_BG          = (15, 23, 42)          # Dark Slate Blue (#0F172A)
    COLOR_PANEL       = (30, 41, 59)          # Slate Card (#1E293B)
    COLOR_HEADER      = (51, 65, 85)         # Header Slate (#334155)
    COLOR_ACCENT      = (255, 191, 0)         # Neon Cyan/Yellow (#00BFFF)
    COLOR_GREEN       = (34, 197, 94)          # Neon Green (#22C55E)
    COLOR_RED         = (239, 68, 68)          # Red (#EF4444)
    COLOR_BLUE        = (246, 147, 59)         # Skeleton Blue (#3B82F6)
    COLOR_AMBER       = (59, 130, 246)         # Amber (#F59E0B)
    COLOR_PURPLE      = (217, 119, 6)          # Indigo (#0677D9)
    COLOR_TEXT_MAIN   = (248, 250, 252)        # White (#F8FAFC)
    COLOR_TEXT_MUTED  = (148, 163, 184)        # Muted Gray (#94A3B8)

    print("[3/4] Rendering side-by-side comparison dashboard frames...")
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        csv_row = csv_rows[frame_idx - 1] if frame_idx <= len(csv_rows) else None

        target_detected = 0
        landmarks_33 = []

        if csv_row:
            target_detected = int(csv_row[2])
            if target_detected == 1:
                raw_lms = csv_row[3:]
                for j in range(33):
                    b = j * 4
                    x, y, z = float(raw_lms[b]), float(raw_lms[b+1]), float(raw_lms[b+2])
                    landmarks_33.append((x, y, z))

        # --- Overlay Video Skeleton & Target Box ---
        if target_detected == 1 and len(landmarks_33) == 33:
            xs = [lm[0] for lm in landmarks_33]
            ys = [lm[1] for lm in landmarks_33]
            min_x, max_x = max(0.0, min(xs)), min(1.0, max(xs))
            min_y, max_y = max(0.0, min(ys)), min(1.0, max(ys))

            px1, py1 = int(min_x * vid_width), int(min_y * vid_height)
            px2, py2 = int(max_x * vid_width), int(max_y * vid_height)

            # Draw Skeleton Connections
            for start_idx, end_idx in MEDIAPIPE_CONNECTIONS:
                p1_x, p1_y = int(landmarks_33[start_idx][0] * vid_width), int(landmarks_33[start_idx][1] * vid_height)
                p2_x, p2_y = int(landmarks_33[end_idx][0] * vid_width), int(landmarks_33[end_idx][1] * vid_height)
                cv2.line(frame, (p1_x, p1_y), (p2_x, p2_y), COLOR_BLUE, 2, cv2.LINE_AA)

            # Draw Joint Landmarks
            for lm in landmarks_33:
                jx, jy = int(lm[0] * vid_width), int(lm[1] * vid_height)
                cv2.circle(frame, (jx, jy), 4, COLOR_GREEN, -1, cv2.LINE_AA)

            # Draw Target Bowler Bounding Box
            cv2.rectangle(frame, (px1, py1), (px2, py2), COLOR_GREEN, 2)
            cv2.putText(frame, "TARGET BOWLER", (px1, max(py1 - 10, 25)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_GREEN, 2, cv2.LINE_AA)
        else:
            cv2.putText(frame, "TARGET LOST", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLOR_RED, 3, cv2.LINE_AA)

        # --- Construct Composite Canvas ---
        canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
        canvas[:, :vid_width] = frame
        canvas[:, vid_width:] = COLOR_BG

        p_left = vid_width + 20
        p_right = canvas_width - 20

        # Header Title Banner
        cv2.rectangle(canvas, (vid_width, 0), (canvas_width, 65), COLOR_HEADER, -1)
        cv2.line(canvas, (vid_width, 65), (canvas_width, 65), COLOR_ACCENT, 2)
        cv2.putText(canvas, "CRICKSENSE: LSTM vs ST-GCN COMPARISON", (p_left, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_TEXT_MAIN, 2, cv2.LINE_AA)

        curr_y = 85

        def draw_card(title: str, items: list, card_y: int, accent_color=COLOR_ACCENT) -> int:
            card_height = 36 + len(items) * 32
            cv2.rectangle(canvas, (p_left, card_y), (p_right, card_y + card_height), COLOR_PANEL, -1)
            cv2.rectangle(canvas, (p_left, card_y), (p_right, card_y + card_height), COLOR_HEADER, 1)

            cv2.putText(canvas, title.upper(), (p_left + 15, card_y + 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, accent_color, 2, cv2.LINE_AA)
            cv2.line(canvas, (p_left + 15, card_y + 30), (p_right - 15, card_y + 30), COLOR_HEADER, 1)

            line_y = card_y + 54
            for key, val, val_color in items:
                cv2.putText(canvas, key, (p_left + 15, line_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.46, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)
                cv2.putText(canvas, str(val), (p_left + 280, line_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.46, val_color, 2 if val_color in [COLOR_GREEN, COLOR_AMBER, COLOR_RED] else 1, cv2.LINE_AA)
                line_y += 30

            return card_y + card_height + 15

        # Section 1: Video Input & Tracking Spec
        status_text = "TARGET DETECTED" if target_detected == 1 else "TARGET LOST"
        status_color = COLOR_GREEN if target_detected == 1 else COLOR_RED

        spec_items = [
            ("Category", "GENERAL", COLOR_TEXT_MAIN),
            ("Input Video", "General1.mp4", COLOR_TEXT_MAIN),
            ("Pose Model", "MediaPipe Pose (33 Joints, X/Y/Z)", COLOR_TEXT_MAIN),
            ("Frame Counter", f"{frame_idx} / {total_frames}", COLOR_TEXT_MAIN),
            ("Target Bowler Status", status_text, status_color),
        ]
        curr_y = draw_card("1. INPUT & SKELETON METADATA", spec_items, curr_y)

        # Section 2: LSTM Section
        lstm_items = [
            ("Architecture", "Recurrent Sequential (1D)", COLOR_TEXT_MAIN),
            ("Input Feature Type", "Temporal Landmark Sequence", COLOR_TEXT_MAIN),
            ("Input Tensor Shape", lstm_in_shape_str, COLOR_TEXT_MAIN),
            ("Output Tensor Shape", lstm_out_shape_str, COLOR_TEXT_MAIN),
            ("LSTM Pipeline Status", "NOT TRAINED", COLOR_AMBER),
            ("LSTM Prediction", "N/A — MODEL NOT TRAINED", COLOR_TEXT_MUTED),
        ]
        curr_y = draw_card("2. LSTM PIPELINE", lstm_items, curr_y, accent_color=COLOR_AMBER)

        # Section 3: ST-GCN Section
        stgcn_items = [
            ("Architecture", "Spatial-Temporal Graph Convolutional Network", COLOR_TEXT_MAIN),
            ("Input Feature Type", "Skeleton Graph Sequence (33 Nodes)", COLOR_TEXT_MAIN),
            ("Input Tensor Shape", stgcn_in_shape_str, COLOR_TEXT_MAIN),
            ("Output Tensor Shape", stgcn_out_shape_str, COLOR_TEXT_MAIN),
            ("Forward Pass Status", "PASS", COLOR_GREEN),
            ("ST-GCN Pipeline Status", "NOT TRAINED", COLOR_AMBER),
            ("ST-GCN Prediction", "N/A — MODEL NOT TRAINED", COLOR_TEXT_MUTED),
        ]
        curr_y = draw_card("3. ST-GCN PIPELINE", stgcn_items, curr_y, accent_color=COLOR_GREEN)

        # Section 4: CRICKSENSE ANALYSIS PANEL (Exact 7 N/A Rows)
        analysis_items = [
            ("Bowling Classification", "N/A — LABEL NOT AVAILABLE", COLOR_TEXT_MUTED),
            ("Good / Bad Bowling", "N/A — LABEL NOT AVAILABLE", COLOR_TEXT_MUTED),
            ("Correct / Incorrect", "N/A — LABEL NOT AVAILABLE", COLOR_TEXT_MUTED),
            ("Accuracy", "N/A — MODEL NOT TRAINED", COLOR_TEXT_MUTED),
            ("Confidence", "N/A — MODEL NOT TRAINED", COLOR_TEXT_MUTED),
            ("Predicted Quality", "N/A — MODEL NOT TRAINED", COLOR_TEXT_MUTED),
            ("ST-GCN Prediction", "N/A — MODEL NOT TRAINED", COLOR_TEXT_MUTED),
        ]
        curr_y = draw_card("4. CRICKSENSE ANALYSIS PANEL", analysis_items, curr_y)

        # Section 5: Comparison Explanation
        comp_items = [
            ("LSTM Approach", "Learns temporal dependencies from sequential landmark data.", COLOR_TEXT_MAIN),
            ("ST-GCN Approach", "Learns spatial joint relationships and temporal movement patterns.", COLOR_TEXT_MAIN),
            ("Performance Evaluation", "Evaluation & comparison will occur after supervised training.", COLOR_TEXT_MUTED),
        ]
        curr_y = draw_card("5. ARCHITECTURE COMPARISON EXPLANATION", comp_items, curr_y)

        # Footer Notice
        cv2.putText(canvas, "* Senior Project Visual Demonstration | Untrained model state preserved.",
                    (p_left + 10, canvas_height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)

        writer.write(canvas)

        if frame_idx % 20 == 0 or frame_idx == total_frames:
            print(f"      Rendered frame {frame_idx}/{total_frames} ({frame_idx/total_frames*100:.1f}%)")

    cap.release()
    writer.release()

    print("\n[4/4] Video processing complete!")
    print(f"      Saved output video to: {output_video_path}")
    print("=" * 80 + "\n")

    # Print summary metrics as requested by prompt
    print("=" * 80)
    print("  MODEL COMPARISON VIDEO GENERATION SUMMARY")
    print("=" * 80)
    print(f"  Output Video Path        : {output_video_path}")
    print(f"  Video Resolution         : {canvas_width} x {canvas_height}")
    print(f"  FPS                      : {fps:.2f}")
    print(f"  Total Frames             : {total_frames}")
    print(f"  Input Tensor Shape (LSTM): {lstm_in_shape_str}")
    print(f"  Input Tensor Shape(STGCN): {stgcn_in_shape_str}")
    print(f"  Output Tensor Shape(LSTM): {lstm_out_shape_str}")
    print(f"  Output Tensor Shape(STGCN: {stgcn_out_shape_str}")
    print(f"  LSTM Status              : {lstm_status}")
    print(f"  ST-GCN Status            : {stgcn_status}")
    print(f"  Forward-Pass Status      : {stgcn_fp_status}")
    print("=" * 80 + "\n")

    return output_video_path


if __name__ == "__main__":
    generate_comparison_video()
