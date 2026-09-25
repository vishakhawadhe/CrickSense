"""
=============================================================================
CrickSense -- General2 Video Visualizer Generator (LSTM & ST-GCN)
=============================================================================
Goal:
    Generate TWO separate demonstration MP4 videos for General2.mp4:
      1. LSTM: ai/output/lstm_general/General2_lstm_demo.mp4
      2. ST-GCN: ai/output/stgcn_general/General2_stgcn_demo.mp4

Requirements:
    - Both use original video ai/data/raw/General/General2.mp4
    - Display bounding box, "TARGET BOWLER", 33 MediaPipe landmarks, 35 skeleton connections
    - Display frame number & detection status
    - Display Category: GENERAL
    - LSTM Video displays LSTM ANALYSIS panel ([1, 177, 99] -> [1, 2])
    - ST-GCN Video displays ST-GCN ANALYSIS panel ([1, 3, 177, 33] -> [1, 2])
    - Both display CRICKSENSE ANALYSIS PANEL with explicit N/A placeholders

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
from typing import Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.stgcn.graph import MEDIAPIPE_CONNECTIONS


def render_general2_demo_video(model_type: str, input_shape_str: str, output_shape_str: str) -> str:
    """
    Render video visualization demo for General2.mp4.
    Args:
        model_type: "LSTM" or "ST-GCN"
        input_shape_str: string representation of input tensor shape
        output_shape_str: string representation of output tensor shape
    Returns:
        output_video_path: path to created video
    """
    raw_video_path = os.path.join(PROJECT_ROOT, "data", "raw", "General", "General2.mp4")
    landmark_csv_path = os.path.join(PROJECT_ROOT, "data", "landmarks", "General", "General2_landmarks.csv")

    if model_type.upper() == "LSTM":
        output_dir = os.path.join(PROJECT_ROOT, "output", "lstm_general")
        output_video_path = os.path.join(output_dir, "General2_lstm_demo.mp4")
        header_title = "CRICKSENSE -- LSTM ANALYSIS"
        card_title = "2. LSTM ANALYSIS"
        input_desc = "Temporal Landmark Sequence"
    else:
        output_dir = os.path.join(PROJECT_ROOT, "output", "stgcn_general")
        output_video_path = os.path.join(output_dir, "General2_stgcn_demo.mp4")
        header_title = "CRICKSENSE -- ST-GCN ANALYSIS"
        card_title = "2. ST-GCN ANALYSIS"
        input_desc = "Skeleton Graph Sequence"

    os.makedirs(output_dir, exist_ok=True)

    print(f"[{model_type}] Processing video feed and rendering overlay...")
    print(f"       Input Video  : {raw_video_path}")
    print(f"       Output Video : {output_video_path}")

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
    csv_rows = reader[1:]  # Skip header

    panel_width = 560
    canvas_width = vid_width + panel_width
    canvas_height = vid_height

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_video_path, fourcc, fps, (canvas_width, canvas_height))

    if not writer.isOpened():
        raise RuntimeError(f"Could not create VideoWriter at: {output_video_path}")

    # Color Palette (BGR)
    COLOR_BG = (15, 23, 42)           # Dark Slate Blue (#0F172A)
    COLOR_PANEL = (30, 41, 59)       # Slate Box (#1E293B)
    COLOR_HEADER = (51, 65, 85)      # Header Slate (#334155)
    COLOR_ACCENT = (255, 191, 0)      # Neon Yellow/Cyan
    COLOR_GREEN = (34, 197, 94)       # Neon Green (#22C55E)
    COLOR_RED = (239, 68, 68)         # Red (#EF4444)
    COLOR_BLUE = (246, 147, 59)       # Skeleton Blue (#3B82F6)
    COLOR_TEXT_MAIN = (248, 250, 252) # White (#F8FAFC)
    COLOR_TEXT_MUTED = (148, 163, 184)# Muted Gray (#94A3B8)

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

        # Draw Skeleton & Bounding Box on Video Feed
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

        # Top Video Header Banner
        banner_sub = np.zeros((100, vid_width, 3), dtype=np.uint8)
        cv2.putText(banner_sub, header_title, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 230, 255), 2, cv2.LINE_AA)
        cv2.putText(banner_sub, "CATEGORY: GENERAL", (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2, cv2.LINE_AA)
        frame[0:100, 0:vid_width] = cv2.addWeighted(frame[0:100, 0:vid_width], 0.3, banner_sub, 0.7, 0)

        # Construct Canvas
        canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
        canvas[:, :vid_width] = frame
        canvas[:, vid_width:] = COLOR_BG

        p_left = vid_width + 20
        p_right = canvas_width - 20

        # Panel Header
        cv2.rectangle(canvas, (vid_width, 0), (canvas_width, 70), COLOR_HEADER, -1)
        cv2.line(canvas, (vid_width, 70), (canvas_width, 70), COLOR_ACCENT, 2)
        cv2.putText(canvas, "CRICKSENSE AI ANALYSIS", (p_left, 44),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_TEXT_MAIN, 2, cv2.LINE_AA)

        curr_y = 100

        def draw_section_card(title: str, items: list, card_y: int) -> int:
            card_height = 40 + len(items) * 36
            cv2.rectangle(canvas, (p_left, card_y), (p_right, card_y + card_height), COLOR_PANEL, -1)
            cv2.rectangle(canvas, (p_left, card_y), (p_right, card_y + card_height), COLOR_HEADER, 1)

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

        # Section 1: Video & Tracking Status
        status_text = "TARGET DETECTED" if target_detected == 1 else "TARGET LOST"
        status_color = COLOR_GREEN if target_detected == 1 else COLOR_RED

        tracking_items = [
            ("Category", "GENERAL", COLOR_TEXT_MAIN),
            ("Input Video", "General2.mp4", COLOR_TEXT_MAIN),
            ("Frame Counter", f"{frame_idx} / {total_frames}", COLOR_TEXT_MAIN),
            ("Tracking Status", status_text, status_color),
        ]
        curr_y = draw_section_card("1. VIDEO & TRACKING STATUS", tracking_items, curr_y)

        # Section 2: Model Analysis Panel
        if model_type.upper() == "LSTM":
            model_items = [
                ("Input", input_desc, COLOR_TEXT_MAIN),
                ("Joints", "33", COLOR_TEXT_MAIN),
                ("Coordinates", "X / Y / Z", COLOR_TEXT_MAIN),
                ("Features per Frame", "99", COLOR_TEXT_MAIN),
                ("Sequence Length", str(total_frames), COLOR_TEXT_MAIN),
                ("Input Tensor", input_shape_str, COLOR_TEXT_MAIN),
                ("LSTM", "ACTIVE", COLOR_GREEN),
                ("Forward Pass", "PASS", COLOR_GREEN),
                ("Model Status", "NOT TRAINED", COLOR_TEXT_MAIN),
                ("Output Tensor", output_shape_str, COLOR_TEXT_MAIN),
                ("Prediction", "N/A -- MODEL NOT TRAINED", COLOR_TEXT_MUTED),
            ]
        else:
            model_items = [
                ("Input", input_desc, COLOR_TEXT_MAIN),
                ("Joints", "33", COLOR_TEXT_MAIN),
                ("Channels", "X / Y / Z", COLOR_TEXT_MAIN),
                ("Sequence Length", str(total_frames), COLOR_TEXT_MAIN),
                ("Input Tensor", input_shape_str, COLOR_TEXT_MAIN),
                ("ST-GCN", "ACTIVE", COLOR_GREEN),
                ("Forward Pass", "PASS", COLOR_GREEN),
                ("Model Status", "NOT TRAINED", COLOR_TEXT_MAIN),
                ("Output Tensor", output_shape_str, COLOR_TEXT_MAIN),
                ("Prediction", "N/A -- MODEL NOT TRAINED", COLOR_TEXT_MUTED),
            ]

        curr_y = draw_section_card(card_title, model_items, curr_y)

        # Section 3: CRICKSENSE ANALYSIS PANEL (Exact display)
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

        if frame_idx % 50 == 0 or frame_idx == total_frames:
            print(f"       Rendered frame {frame_idx}/{total_frames} ({frame_idx/total_frames*100:.1f}%)")

    cap.release()
    writer.release()
    print(f"       Video created successfully: {output_video_path}\n")
    return output_video_path
