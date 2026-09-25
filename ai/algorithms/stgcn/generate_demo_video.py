"""
=============================================================================
CrickSense -- ST-GCN General Category Video Visualization & Analysis Dashboard
=============================================================================
Goal:
    Generate a full-featured video demonstration MP4 showing:
      1. Original bowling video feed
      2. Target bowler bounding box & "TARGET BOWLER" overlay
      3. All 33 MediaPipe body landmarks and 35 skeleton connections
      4. Live frame counter & detection status
      5. Category: GENERAL tag
      6. ST-GCN Technical Pipeline Status Panel (Active, Tensor Shapes, Forward Pass)
      7. CrickSense Analysis Result Panel displaying real calculated output tensor
         and explicit "N/A — MODEL NOT TRAINED" / "N/A — LABEL NOT AVAILABLE"
         for unavailable metrics.

Input:
    ai/data/raw/General/General1.mp4
    ai/data/landmarks/General/General1_landmarks.csv

Output:
    ai/output/stgcn_general/General1_stgcn_demo.mp4

Author : CrickSense Team
Date   : 2026
=============================================================================
"""

import os
import sys
import csv
import cv2
import torch
import numpy as np

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.stgcn.graph import MediaPipeGraph, MEDIAPIPE_CONNECTIONS
from algorithms.stgcn.model import STGCNModel
from algorithms.stgcn.test_stgcn import load_landmark_csv


def generate_stgcn_demo_video():
    raw_video_path = os.path.join(PROJECT_ROOT, "data", "raw", "General", "General1.mp4")
    landmark_csv_path = os.path.join(PROJECT_ROOT, "data", "landmarks", "General", "General1_landmarks.csv")
    output_dir = os.path.join(PROJECT_ROOT, "output", "stgcn_general")
    output_video_path = os.path.join(output_dir, "General1_stgcn_demo.mp4")

    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 80)
    print("  CrickSense -- ST-GCN General Category Demo Video Generator")
    print("=" * 80)
    print(f"  Input Video  : {raw_video_path}")
    print(f"  Landmark CSV : {landmark_csv_path}")
    print(f"  Output Video : {output_video_path}")
    print("=" * 80 + "\n")

    # Step 1: Run ST-GCN Model Forward Pass on actual landmark CSV
    print("[1/4] Running ST-GCN model forward pass on landmark sequence...")
    data_c_t_v, T, V = load_landmark_csv(landmark_csv_path, channels=3)
    tensor_input = torch.from_numpy(data_c_t_v).unsqueeze(0)  # Shape: (1, 3, T, V)

    graph = MediaPipeGraph(strategy="spatial")
    model = STGCNModel(in_channels=3, num_classes=2, graph_adjacency=graph.A)
    model.eval()

    with torch.no_grad():
        output_tensor = model(tensor_input)

    input_shape_str = f"[{tensor_input.shape[0]}, {tensor_input.shape[1]}, {tensor_input.shape[2]}, {tensor_input.shape[3]}]"
    output_shape_str = f"[{output_tensor.shape[0]}, {output_tensor.shape[1]}]"
    raw_out_vals = output_tensor.numpy()[0]
    raw_out_str = f"[{raw_out_vals[0]:.3f}, {raw_out_vals[1]:.3f}]"

    print(f"      Input Tensor Shape  : {input_shape_str}")
    print(f"      Output Tensor Shape : {output_shape_str}")
    print(f"      Raw ST-GCN Output   : {raw_out_str}")
    print("      Forward Pass Status : PASS\n")

    # Step 2: Open Video File
    print("[2/4] Opening video file and loading landmark data...")
    cap = cv2.VideoCapture(raw_video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {raw_video_path}")

    vid_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or np.isnan(fps):
        fps = 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Read CSV landmark rows
    with open(landmark_csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
    csv_rows = reader[1:]  # Skip header

    # Step 3: Setup Video Writer with Dashboard Canvas
    # Panel width = 560px, Total canvas = vid_width + 560 x vid_height
    panel_width = 560
    canvas_width = vid_width + panel_width
    canvas_height = vid_height

    print(f"      Video Canvas Resolution: {canvas_width} x {canvas_height} @ {fps:.2f} FPS")

    # Codec choice (mp4v)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_video_path, fourcc, fps, (canvas_width, canvas_height))

    if not writer.isOpened():
        raise RuntimeError(f"Could not create VideoWriter: {output_video_path}")

    # Colors (BGR)
    COLOR_BG = (15, 23, 42)          # Dark Slate Blue (#0F172A)
    COLOR_PANEL = (30, 41, 59)      # Slate Box (#1E293B)
    COLOR_HEADER = (51, 65, 85)     # Header Slate (#334155)
    COLOR_ACCENT = (255, 191, 0)     # Neon Cyan/Yellow accent
    COLOR_GREEN = (34, 197, 94)      # Neon Green (#22C55E)
    COLOR_RED = (239, 68, 68)        # Red (#EF4444)
    COLOR_BLUE = (246, 147, 59)      # Skeleton Blue (#3B82F6)
    COLOR_TEXT_MAIN = (248, 250, 252)# White (#F8FAFC)
    COLOR_TEXT_MUTED = (148, 163, 184) # Muted Gray (#94A3B8)
    COLOR_TEXT_AMBER = (59, 130, 246)  # Amber (#F59E0B)

    print("[3/4] Processing frames and rendering UI overlay...")
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

        # --- Draw Video Skeleton & Bounding Box ---
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
            # Render TARGET LOST Banner
            cv2.putText(frame, "TARGET LOST", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLOR_RED, 3, cv2.LINE_AA)

        # --- Construct Composite Canvas ---
        canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
        canvas[:, :vid_width] = frame

        # Fill Dashboard Background
        canvas[:, vid_width:] = COLOR_BG

        # Panel Header Box
        p_left = vid_width + 20
        p_top = 20
        p_right = canvas_width - 20

        # Header Title
        cv2.rectangle(canvas, (vid_width, 0), (canvas_width, 70), COLOR_HEADER, -1)
        cv2.line(canvas, (vid_width, 70), (canvas_width, 70), COLOR_ACCENT, 2)
        cv2.putText(canvas, "CRICKSENSE AI ANALYSIS", (p_left, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_TEXT_MAIN, 2, cv2.LINE_AA)

        curr_y = 105

        def draw_section_card(title: str, items: list, card_y: int) -> int:
            """Draw a dashboard card with key-value pairs."""
            card_height = 40 + len(items) * 36
            cv2.rectangle(canvas, (p_left, card_y), (p_right, card_y + card_height), COLOR_PANEL, -1)
            cv2.rectangle(canvas, (p_left, card_y), (p_right, card_y + card_height), COLOR_HEADER, 1)

            # Title Header Line
            cv2.putText(canvas, title.upper(), (p_left + 15, card_y + 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_ACCENT, 2, cv2.LINE_AA)
            cv2.line(canvas, (p_left + 15, card_y + 36), (p_right - 15, card_y + 36), COLOR_HEADER, 1)

            line_y = card_y + 65
            for key, val, val_color in items:
                cv2.putText(canvas, key, (p_left + 15, line_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)
                cv2.putText(canvas, str(val), (p_left + 230, line_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, val_color, 2 if val_color != COLOR_TEXT_MUTED else 1, cv2.LINE_AA)
                line_y += 34

            return card_y + card_height + 20

        # Card 1: Video & Tracking Status
        status_text = "TARGET DETECTED" if target_detected == 1 else "TARGET LOST"
        status_color = COLOR_GREEN if target_detected == 1 else COLOR_RED

        tracking_items = [
            ("Category", "GENERAL", COLOR_TEXT_MAIN),
            ("Input Video", "General1.mp4", COLOR_TEXT_MAIN),
            ("Frame Counter", f"{frame_idx} / {total_frames}", COLOR_TEXT_MAIN),
            ("Tracking Status", status_text, status_color),
        ]
        curr_y = draw_section_card("1. VIDEO & TRACKING STATUS", tracking_items, curr_y)

        # Card 2: ST-GCN Technical Pipeline Status
        stgcn_items = [
            ("ST-GCN Module", "ACTIVE", COLOR_GREEN),
            ("Input Channels", "33 Joints (X, Y, Z)", COLOR_TEXT_MAIN),
            ("Input Tensor Shape", input_shape_str, COLOR_TEXT_MAIN),
            ("Output Tensor Shape", output_shape_str, COLOR_TEXT_MAIN),
            ("Forward Pass", "PASS", COLOR_GREEN),
            ("Raw ST-GCN Tensor", raw_out_str, COLOR_TEXT_MAIN),
        ]
        curr_y = draw_section_card("2. ST-GCN PIPELINE STATUS", stgcn_items, curr_y)

        # Card 3: CrickSense Analysis Result Panel
        analysis_items = [
            ("Bowling Classification", "N/A — LABEL NOT AVAILABLE", COLOR_TEXT_MUTED),
            ("Good / Bad Bowling", "N/A — LABEL NOT AVAILABLE", COLOR_TEXT_MUTED),
            ("Correct / Incorrect", "N/A — LABEL NOT AVAILABLE", COLOR_TEXT_MUTED),
            ("Accuracy", "N/A — MODEL NOT TRAINED", COLOR_TEXT_MUTED),
            ("Confidence", "N/A — MODEL NOT TRAINED", COLOR_TEXT_MUTED),
            ("Predicted Quality", "N/A — MODEL NOT TRAINED", COLOR_TEXT_MUTED),
            ("ST-GCN Prediction", "N/A — MODEL NOT TRAINED", COLOR_TEXT_MUTED),
        ]
        curr_y = draw_section_card("3. CRICKSENSE ANALYSIS PANEL", analysis_items, curr_y)

        # Footer Disclaimer Notice
        cv2.putText(canvas, "* Note: Model output is untrained. Real tensor values shown.",
                    (p_left + 10, canvas_height - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)

        writer.write(canvas)

        if frame_idx % 20 == 0 or frame_idx == total_frames:
            print(f"      Rendered frame {frame_idx}/{total_frames} ({frame_idx/total_frames*100:.1f}%)")

    cap.release()
    writer.release()
    print("\n[4/4] Video processing complete!")
    print(f"      Saved output video to: {output_video_path}")
    print("=" * 80 + "\n")

    return output_video_path


if __name__ == "__main__":
    generate_stgcn_demo_video()
