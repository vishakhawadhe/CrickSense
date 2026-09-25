"""
=============================================================================
CrickSense -- LSTM General Category Visualization & Analysis Dashboard Generator
=============================================================================
Goal:
    Generate a playable MP4 video demonstration showing:
      1. Original bowling video feed (General1.mp4)
      2. Header banner overlay: "CRICKSENSE — LSTM ANALYSIS" & "CATEGORY: GENERAL"
      3. Target bowler bounding box & "TARGET BOWLER" label overlay
      4. All 33 MediaPipe body landmarks and 35 skeleton connections
      5. Frame counter & detection status
      6. Section 2: LSTM ANALYSIS status card (Active, Tensor Shapes, Forward Pass, Not Trained)
      7. Section 3: CRICKSENSE ANALYSIS PANEL displaying explicit N/A placeholders

Input:
    ai/data/raw/General/General1.mp4
    ai/data/landmarks/General/General1_landmarks.csv

Output:
    ai/output/lstm_general/General1_lstm_demo.mp4

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
from typing import Tuple, List

# Add project root to python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.lstm.model import BowlingLSTM
from algorithms.stgcn.graph import MEDIAPIPE_CONNECTIONS


def load_lstm_landmark_csv(csv_path: str) -> Tuple[np.ndarray, int, int, int]:
    """
    Load landmark coordinates from CSV for LSTM input tensor generation.
    Returns:
        data_np: numpy array of shape (T, 99)
        total_frames: integer T
        valid_frames: count of target_detected == 1
        lost_frames: count of target_detected == 0
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Landmark CSV file not found: {csv_path}")

    frames_data = []
    valid_frames = 0
    lost_frames = 0

    with open(csv_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)

        for row in reader:
            if not row:
                continue
            
            target_detected = int(row[2])
            raw_landmarks = row[3:]

            if target_detected == 1:
                valid_frames += 1
            else:
                lost_frames += 1

            frame_features = []
            for j in range(33):
                base_idx = j * 4
                if target_detected == 1:
                    x = float(raw_landmarks[base_idx])
                    y = float(raw_landmarks[base_idx + 1])
                    z = float(raw_landmarks[base_idx + 2])
                else:
                    # Target lost fallback: 0.0 feature fill
                    x, y, z = 0.0, 0.0, 0.0
                frame_features.extend([x, y, z])

            frames_data.append(frame_features)  # 99 features

    data_np = np.array(frames_data, dtype=np.float32)  # Shape: (T, 99)
    total_frames = len(data_np)
    return data_np, total_frames, valid_frames, lost_frames


def generate_lstm_demo_video() -> str:
    """Generate playable MP4 video with overlay and dashboard panel."""
    raw_video_path = os.path.join(PROJECT_ROOT, "data", "raw", "General", "General1.mp4")
    landmark_csv_path = os.path.join(PROJECT_ROOT, "data", "landmarks", "General", "General1_landmarks.csv")
    output_dir = os.path.join(PROJECT_ROOT, "output", "lstm_general")
    output_video_path = os.path.join(output_dir, "General1_lstm_demo.mp4")

    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 80)
    print("  CrickSense -- LSTM General Category Demo Video Generator")
    print("=" * 80)
    print(f"  Input Video  : {raw_video_path}")
    print(f"  Landmark CSV : {landmark_csv_path}")
    print(f"  Output Video : {output_video_path}")
    print("=" * 80 + "\n")

    # Step 1: Run LSTM Model Forward Pass
    print("[1/4] Loading landmarks and executing LSTM forward pass...")
    data_t_99, total_frames, valid_frames, lost_frames = load_lstm_landmark_csv(landmark_csv_path)
    
    # Input tensor shape [1, T, 99]
    input_tensor = torch.from_numpy(data_t_99).unsqueeze(0)  # Shape: [1, T, 99]
    T = input_tensor.shape[1]

    model = BowlingLSTM(input_size=99, hidden_size=128, num_layers=2, num_classes=2)
    model.eval()

    with torch.no_grad():
        output_tensor = model(input_tensor)

    input_shape_str = f"[{input_tensor.shape[0]}, {input_tensor.shape[1]}, {input_tensor.shape[2]}]"
    output_shape_str = f"[{output_tensor.shape[0]}, {output_tensor.shape[1]}]"

    print(f"      Sequence Length (T) : {T}")
    print(f"      Input Tensor Shape  : {input_shape_str}")
    print(f"      Output Tensor Shape : {output_shape_str}")
    print("      Forward Pass Status : PASS\n")

    # Step 2: Open Video Reader & Read Landmark Rows
    print("[2/4] Opening raw video feed...")
    cap = cv2.VideoCapture(raw_video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {raw_video_path}")

    vid_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or np.isnan(fps):
        fps = 30.0

    with open(landmark_csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
    csv_rows = reader[1:]  # Skip header

    # Canvas dimensions
    panel_width = 560
    canvas_width = vid_width + panel_width
    canvas_height = vid_height

    print(f"      Resolution: {canvas_width} x {canvas_height} @ {fps:.2f} FPS")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_video_path, fourcc, fps, (canvas_width, canvas_height))

    if not writer.isOpened():
        raise RuntimeError(f"Could not create VideoWriter at: {output_video_path}")

    # Color Palette (BGR format)
    COLOR_BG = (15, 23, 42)           # Dark Slate Blue (#0F172A)
    COLOR_PANEL = (30, 41, 59)       # Slate Box (#1E293B)
    COLOR_HEADER = (51, 65, 85)      # Header Slate (#334155)
    COLOR_ACCENT = (255, 191, 0)      # Neon Yellow/Cyan
    COLOR_GREEN = (34, 197, 94)       # Neon Green (#22C55E)
    COLOR_RED = (239, 68, 68)         # Red (#EF4444)
    COLOR_BLUE = (246, 147, 59)       # Skeleton Blue/Cyan (#3B82F6)
    COLOR_TEXT_MAIN = (248, 250, 252) # Main White (#F8FAFC)
    COLOR_TEXT_MUTED = (148, 163, 184)# Muted Gray (#94A3B8)
    COLOR_OVERLAY_BG = (0, 0, 0)      # Black overlay banner

    print("[3/4] Rendering frames and writing video output...")
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

        # --- Draw Video Skeleton & Overlays ---
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
            cv2.putText(frame, "TARGET LOST", (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLOR_RED, 3, cv2.LINE_AA)

        # Top Video Overlay Banner required:
        # CRICKSENSE — LSTM ANALYSIS
        # CATEGORY: GENERAL
        banner_sub = np.zeros((100, vid_width, 3), dtype=np.uint8)
        cv2.putText(banner_sub, "CRICKSENSE -- LSTM ANALYSIS", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 230, 255), 2, cv2.LINE_AA)
        cv2.putText(banner_sub, "CATEGORY: GENERAL", (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2, cv2.LINE_AA)
        # Blend banner onto top of frame
        frame[0:100, 0:vid_width] = cv2.addWeighted(frame[0:100, 0:vid_width], 0.3, banner_sub, 0.7, 0)

        # --- Construct Composite Canvas ---
        canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
        canvas[:, :vid_width] = frame

        # Fill Dashboard Panel Background
        canvas[:, vid_width:] = COLOR_BG

        # Panel Header Box
        p_left = vid_width + 20
        p_right = canvas_width - 20

        # Header Title
        cv2.rectangle(canvas, (vid_width, 0), (canvas_width, 70), COLOR_HEADER, -1)
        cv2.line(canvas, (vid_width, 70), (canvas_width, 70), COLOR_ACCENT, 2)
        cv2.putText(canvas, "CRICKSENSE AI ANALYSIS", (p_left, 44),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_TEXT_MAIN, 2, cv2.LINE_AA)

        curr_y = 100

        def draw_section_card(title: str, items: list, card_y: int) -> int:
            """Helper to render dashboard section cards."""
            card_height = 40 + len(items) * 36
            cv2.rectangle(canvas, (p_left, card_y), (p_right, card_y + card_height), COLOR_PANEL, -1)
            cv2.rectangle(canvas, (p_left, card_y), (p_right, card_y + card_height), COLOR_HEADER, 1)

            # Section Title Header Line
            cv2.putText(canvas, title.upper(), (p_left + 15, card_y + 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_ACCENT, 2, cv2.LINE_AA)
            cv2.line(canvas, (p_left + 15, card_y + 36), (p_right - 15, card_y + 36), COLOR_HEADER, 1)

            line_y = card_y + 65
            for key, val, val_color in items:
                cv2.putText(canvas, key, (p_left + 15, line_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TEXT_MUTED, 1, cv2.LINE_AA)
                cv2.putText(canvas, str(val), (p_left + 225, line_y),
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

        # Card 2: LSTM ANALYSIS Panel
        lstm_items = [
            ("Input", "Temporal Landmark Sequence", COLOR_TEXT_MAIN),
            ("Joints", "33", COLOR_TEXT_MAIN),
            ("Coordinates", "X / Y / Z", COLOR_TEXT_MAIN),
            ("Features per Frame", "99", COLOR_TEXT_MAIN),
            ("Sequence Length", str(T), COLOR_TEXT_MAIN),
            ("Input Tensor", input_shape_str, COLOR_TEXT_MAIN),
            ("LSTM", "ACTIVE", COLOR_GREEN),
            ("Forward Pass", "PASS", COLOR_GREEN),
            ("Model Status", "NOT TRAINED", COLOR_TEXT_MAIN),
            ("Output Tensor", output_shape_str, COLOR_TEXT_MAIN),
            ("Prediction", "N/A -- MODEL NOT TRAINED", COLOR_TEXT_MUTED),
        ]
        curr_y = draw_section_card("2. LSTM ANALYSIS", lstm_items, curr_y)

        # Card 3: CRICKSENSE ANALYSIS PANEL (Exact display)
        analysis_items = [
            ("Bowling Classification", "N/A -- LABEL NOT AVAILABLE", COLOR_TEXT_MUTED),
            ("Good / Bad Bowling", "N/A -- LABEL NOT AVAILABLE", COLOR_TEXT_MUTED),
            ("Correct / Incorrect", "N/A -- LABEL NOT AVAILABLE", COLOR_TEXT_MUTED),
            ("Accuracy", "N/A -- MODEL NOT TRAINED", COLOR_TEXT_MUTED),
            ("Confidence", "N/A -- MODEL NOT TRAINED", COLOR_TEXT_MUTED),
            ("Predicted Quality", "N/A -- MODEL NOT TRAINED", COLOR_TEXT_MUTED),
            ("ST-GCN Prediction", "N/A -- MODEL NOT TRAINED", COLOR_TEXT_MUTED),
        ]
        curr_y = draw_section_card("3. CRICKSENSE ANALYSIS PANEL", analysis_items, curr_y)

        writer.write(canvas)

        if frame_idx % 25 == 0 or frame_idx == total_frames:
            print(f"      Rendered frame {frame_idx}/{total_frames} ({frame_idx/total_frames*100:.1f}%)")

    cap.release()
    writer.release()
    print("\n[4/4] Video processing complete!")
    print(f"      Saved output video to: {output_video_path}")
    print("=" * 80 + "\n")

    return output_video_path


if __name__ == "__main__":
    generate_lstm_demo_video()
