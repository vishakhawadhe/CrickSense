"""
=============================================================================
CrickSense -- Step 1: OpenCV + MediaPipe Pose Detection Test
=============================================================================
Goal:
    Verify that OpenCV can read a bowling video and MediaPipe (BlazePose /
    PoseLandmarker) can successfully detect the player's 33 body landmarks
    frame-by-frame.

MediaPipe version compatibility note:
    This script uses MediaPipe >= 1.0.0  which uses the NEW Tasks API:
        - mediapipe.tasks.python.vision.PoseLandmarker
        - mediapipe.tasks.python.core.BaseOptions
    The old mp.solutions.pose API was removed in MediaPipe 1.0.0.
    A pre-trained .task model file is required (downloaded separately).

Pipeline:
    Bowling Video
          |
      OpenCV  (reads frames)
          |
    Frame Extraction
          |
    MediaPipe PoseLandmarker  (detects body landmarks)
          |
    33 Body Landmarks
          |
    Skeleton Overlay  (drawn back onto frame via OpenCV)
          |
    Output Video  (saved as output/output_pose_v1.mp4)

Author : CrickSense Team
Date   : 2026
=============================================================================
"""

import cv2
import mediapipe as mp
import os
import sys
import numpy as np
from typing import Any, Optional, Tuple, List, Dict

# MediaPipe 1.0.x Tasks API imports (compatible with mediapipe >= 1.0.0)
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode
PoseLandmarksConnections = mp.tasks.vision.PoseLandmarksConnections
drawing_utils = mp.tasks.vision.drawing_utils
drawing_styles = mp.tasks.vision.drawing_styles
BaseOptions = mp.tasks.BaseOptions


# ---------------------------------------------------------------------------
# CONFIGURATION -- edit these paths if needed, or pass as CLI arguments
# ---------------------------------------------------------------------------

# Input video path -- default to bowling_v1.mp4, or pass via command line argument 1
INPUT_VIDEO_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "videos", "bowling_v1.mp4")

# Output video path -- default to output_pose_v1.mp4, or pass via command line argument 2
OUTPUT_VIDEO_PATH = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "output", "output_pose_v1.mp4")

# MediaPipe PoseLandmarker model file (download once, keep in models/)
# Download from:
#   https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "pose_landmarker_full.task")

# Drawing colours (BGR format for OpenCV)
LANDMARK_COLOR   = (0, 255, 0)    # Green dots for joints
CONNECTION_COLOR = (255, 0, 0)    # Blue lines for bones
LANDMARK_THICKNESS   = 2
CONNECTION_THICKNESS = 2
LANDMARK_RADIUS      = 4


# ---------------------------------------------------------------------------
# STEP 1 -- VALIDATE PATHS
# ---------------------------------------------------------------------------

def validate_paths():
    """
    Check that the model file and input video exist before we start.
    Print clear instructions if anything is missing.
    """
    ok = True

    if not os.path.exists(MODEL_PATH):
        print(f"\n[ERROR] MediaPipe model file NOT FOUND:")
        print(f"        {MODEL_PATH}")
        print()
        print("  Download it with this PowerShell command:")
        print("  New-Item -ItemType Directory -Path ai\\models -Force")
        print("  Invoke-WebRequest -Uri \\")
        print("    'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task' \\")
        print("    -OutFile ai\\models\\pose_landmarker_full.task -UseBasicParsing")
        ok = False

    if not os.path.exists(INPUT_VIDEO_PATH):
        print(f"\n[ERROR] Video file NOT FOUND:")
        print(f"        {INPUT_VIDEO_PATH}")
        print(f"        Place your bowling video at that path.")
        ok = False

    return ok


# ---------------------------------------------------------------------------
# STEP 2 -- OPEN THE VIDEO WITH OPENCV
# ---------------------------------------------------------------------------

def open_video(path: str) -> cv2.VideoCapture:
    """
    Open the video file using OpenCV and return the VideoCapture object.
    Exits the program if the file cannot be opened.
    """
    cap = cv2.VideoCapture(path)

    if not cap.isOpened():
        print(f"\n[ERROR] OpenCV could not open the video: {path}")
        sys.exit(1)

    return cap


def print_video_info(cap: cv2.VideoCapture, path: str):
    """
    Read and print basic metadata about the video:
        - File path
        - FPS (frames per second)
        - Total number of frames
        - Resolution (width x height)
        - Duration in seconds
    """
    fps          = cap.get(cv2.CAP_PROP_FPS)                # Frames per second
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))   # Total frame count
    width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # Frame width in pixels
    height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Frame height in pixels
    duration_sec = total_frames / fps if fps > 0 else 0     # Duration in seconds

    print("\n" + "=" * 60)
    print("  CrickSense -- Video Information")
    print("=" * 60)
    print(f"  File       : {os.path.basename(path)}")
    print(f"  FPS        : {fps:.2f}")
    print(f"  Frames     : {total_frames}")
    print(f"  Resolution : {width} x {height} pixels")
    print(f"  Duration   : {duration_sec:.2f} seconds  ({duration_sec/60:.2f} minutes)")
    print("=" * 60 + "\n")

    return fps, total_frames, width, height


# ---------------------------------------------------------------------------
# STEP 3 -- SET UP THE OUTPUT VIDEO WRITER
# ---------------------------------------------------------------------------

def create_video_writer(output_path: str, fps: float, width: int, height: int) -> cv2.VideoWriter:
    """
    Create an OpenCV VideoWriter to save the processed frames as a new .mp4.
    'mp4v' is the codec used to encode the output video.
    """
    fourcc = cv2.VideoWriter.fourcc(*"mp4v")  # MP4 codec
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not writer.isOpened():
        print(f"\n[ERROR] Could not create output video: {output_path}")
        sys.exit(1)

    print(f"[INFO] Output video will be saved to: {output_path}\n")
    return writer


# ---------------------------------------------------------------------------
# STEP 4 -- TARGET BOWLER TRACKER & VISUAL OVERLAY
# ---------------------------------------------------------------------------

class TargetBowlerTracker:
    """
    Single-Target Bowler Tracker with Anti-Switching Security.

    Features:
      1. Initial Lock-on: Filter for upright central athletes (height >= 0.18, area >= 0.015).
      2. Persistent Memory: Retain target center, height, area, and velocity vector across frames.
      3. Multi-Metric Matching: Centroid distance + log ratio of height/area scale similarity.
      4. Strict Tracking Gate: Match IF distance <= 0.22 and scale difference <= 0.8.
         Otherwise, return None (TARGET LOST). NEVER switch to another candidate pose.
    """
    def __init__(self) -> None:
        self.is_locked: bool = False
        self.target_center: Optional[Tuple[float, float]] = None
        self.target_height: Optional[float] = None
        self.target_area: Optional[float] = None
        self.velocity: List[float] = [0.0, 0.0]
        self.lost_counter: int = 0
        self.max_lost_frames: int = 45

    def select_target(self, pose_landmarks_list: List[Any]) -> Tuple[Optional[Any], Optional[Tuple[float, float, float, float]]]:
        if not pose_landmarks_list:
            self._handle_loss()
            return None, None

        candidates: List[Dict[str, Any]] = []
        for pose in pose_landmarks_list:
            xs = [lm.x for lm in pose]
            ys = [lm.y for lm in pose]
            min_x, max_x = max(0.0, min(xs)), min(1.0, max(xs))
            min_y, max_y = max(0.0, min(ys)), min(1.0, max(ys))
            width = max_x - min_x
            height = max_y - min_y
            area = width * height
            cx = (min_x + max_x) / 2.0
            cy = (min_y + max_y) / 2.0
            candidates.append({
                'pose': pose,
                'bbox': (min_x, min_y, max_x, max_y),
                'width': width,
                'height': height,
                'area': area,
                'center': (cx, cy)
            })

        if not self.is_locked or self.lost_counter > self.max_lost_frames:
            valid_initial: List[Tuple[float, Dict[str, Any]]] = []
            for c in candidates:
                dist_center_x = abs(c['center'][0] - 0.5)
                if c['height'] >= 0.18 and c['area'] >= 0.015 and dist_center_x <= 0.35:
                    score = (c['height'] * c['width']) / (1.0 + 3.0 * dist_center_x + 1.0 * abs(c['center'][1] - 0.55))
                    valid_initial.append((score, c))

            if not valid_initial:
                for c in candidates:
                    dist_center_x = abs(c['center'][0] - 0.5)
                    if c['height'] >= 0.15:
                        score = c['area'] / (1.0 + 2.0 * dist_center_x)
                        valid_initial.append((score, c))

            if not valid_initial:
                self._handle_loss()
                return None, None

            best_score, best = max(valid_initial, key=lambda item: item[0])
            self._lock_onto(best)
            return best['pose'], best['bbox']

        else:
            if self.target_center is None or self.target_height is None or self.target_area is None:
                self._handle_loss()
                return None, None

            target_center = self.target_center
            target_height = self.target_height
            target_area = self.target_area

            pred_cx = target_center[0] + self.velocity[0]
            pred_cy = target_center[1] + self.velocity[1]

            best_candidate: Optional[Dict[str, Any]] = None
            best_cost = float('inf')

            for c in candidates:
                dx = c['center'][0] - pred_cx
                dy = c['center'][1] - pred_cy
                pos_dist = (dx * dx + dy * dy) ** 0.5

                c_h: float = float(c['height'])
                c_a: float = float(c['area'])
                h_ratio = abs(np.log(max(c_h, 1e-5) / max(target_height, 1e-5)))
                a_ratio = abs(np.log(max(c_a, 1e-5) / max(target_area, 1e-5)))
                scale_dist = h_ratio + a_ratio

                total_cost = pos_dist + 0.3 * scale_dist

                if pos_dist <= 0.22 and scale_dist <= 0.8:
                    if total_cost < best_cost:
                        best_cost = total_cost
                        best_candidate = c

            if best_candidate is not None:
                self._update_target(best_candidate)
                return best_candidate['pose'], best_candidate['bbox']
            else:
                self._handle_loss()
                return None, None

    def _lock_onto(self, candidate: Dict[str, Any]) -> None:
        self.is_locked = True
        self.target_center = candidate['center']
        self.target_height = float(candidate['height'])
        self.target_area = float(candidate['area'])
        self.velocity = [0.0, 0.0]
        self.lost_counter = 0

    def _update_target(self, candidate: Dict[str, Any]) -> None:
        if self.target_center is None or self.target_height is None or self.target_area is None:
            self._lock_onto(candidate)
            return

        new_cx, new_cy = candidate['center']
        old_cx, old_cy = self.target_center
        vx = 0.6 * self.velocity[0] + 0.4 * (new_cx - old_cx)
        vy = 0.6 * self.velocity[1] + 0.4 * (new_cy - old_cy)

        self.target_center = (
            0.7 * old_cx + 0.3 * new_cx,
            0.7 * old_cy + 0.3 * new_cy
        )
        self.target_height = 0.7 * self.target_height + 0.3 * float(candidate['height'])
        self.target_area = 0.7 * self.target_area + 0.3 * float(candidate['area'])
        self.velocity = [vx, vy]
        self.lost_counter = 0

    def _handle_loss(self) -> None:
        self.lost_counter += 1
        if self.target_center is not None:
            self.target_center = (
                self.target_center[0] + self.velocity[0] * 0.8,
                self.target_center[1] + self.velocity[1] * 0.8
            )
            self.velocity = [self.velocity[0] * 0.8, self.velocity[1] * 0.8]


def draw_pose_on_frame(frame: np.ndarray, target_landmarks, target_bbox) -> int:
    """
    Draw MediaPipe 33-landmark skeleton overlay ONLY for the selected target bowler.
    In visual verification mode:
      - Target Selected: Draws green skeleton, green bounding box, and 'TARGET BOWLER' text.
      - Target Lost: Draws NO skeleton, NO box, and renders red 'TARGET LOST' banner.

    Returns the number of landmarks drawn (33 if target selected, 0 if lost).
    """
    if target_landmarks is None:
        cv2.putText(
            frame, "TARGET LOST", (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3, cv2.LINE_AA
        )
        return 0

    drawing_utils.draw_landmarks(
        image=frame,
        landmark_list=target_landmarks,
        connections=PoseLandmarksConnections.POSE_LANDMARKS,
        landmark_drawing_spec=drawing_utils.DrawingSpec(
            color=LANDMARK_COLOR,
            thickness=LANDMARK_THICKNESS,
            circle_radius=LANDMARK_RADIUS,
        ),
        connection_drawing_spec=drawing_utils.DrawingSpec(
            color=CONNECTION_COLOR,
            thickness=CONNECTION_THICKNESS,
        ),
    )

    if target_bbox is not None:
        h, w, _ = frame.shape
        min_x, min_y, max_x, max_y = target_bbox
        px1, py1 = int(min_x * w), int(min_y * h)
        px2, py2 = int(max_x * w), int(max_y * h)

        cv2.rectangle(frame, (px1, py1), (px2, py2), (0, 255, 0), 2)

        label = "TARGET BOWLER"
        label_y = max(py1 - 10, 25)
        cv2.putText(
            frame, label, (px1, label_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA
        )

    return len(target_landmarks)


# ---------------------------------------------------------------------------
# STEP 5 -- MAIN PROCESSING LOOP
# ---------------------------------------------------------------------------

def process_video(cap: cv2.VideoCapture,
                  writer: cv2.VideoWriter,
                  total_frames: int,
                  pose_landmarker: Any):
    """
    Main loop:
        1. Read each frame from the video using OpenCV.
        2. Convert the frame to a MediaPipe Image object.
        3. Pass it to PoseLandmarker for multi-person detection.
        4. Select ONLY the target bowler using persistent TargetBowlerTracker.
        5. Draw skeleton, bounding box, and label ONLY for the selected bowler.
        6. If lost, render red TARGET LOST banner without switching identity.
        7. Write the processed frame to the output video.
    """
    frame_index = 0
    total_candidates_detected = 0
    target_detected_count = 0
    target_lost_count = 0
    tracker = TargetBowlerTracker()

    print("[INFO] Starting frame-by-frame processing...\n")
    print(f"{'Frame':>6}  {'Candidates':>10}  {'Target Bowler Status'}")
    print("-" * 50)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("\n[INFO] End of video reached.")
            break

        frame_index += 1

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        detection_result = pose_landmarker.detect(mp_image)
        pose_landmarks_list = detection_result.pose_landmarks if detection_result.pose_landmarks else []
        num_candidates = len(pose_landmarks_list)
        total_candidates_detected += num_candidates

        # Select target bowler
        target_landmarks, target_bbox = tracker.select_target(pose_landmarks_list)

        # Draw overlay for target bowler only or TARGET LOST banner
        num_landmarks_drawn = draw_pose_on_frame(frame, target_landmarks, target_bbox)

        if num_landmarks_drawn > 0:
            status = "Target Selected"
            target_detected_count += 1
        else:
            status = "Target Lost"
            target_lost_count += 1

        print(f"{frame_index:>6}  {num_candidates:>10}  {status}")
        writer.write(frame)

        if frame_index % 50 == 0:
            pct = (frame_index / total_frames) * 100 if total_frames > 0 else 0
            print(f"\n  [Progress] {frame_index}/{total_frames} frames  ({pct:.1f}%)\n")

    return frame_index, total_candidates_detected, target_detected_count, target_lost_count


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 60)
    print("  CrickSense -- Step 1: Pose Detection & Target Selection Test")
    print(f"  MediaPipe version : {mp.__version__}")
    print(f"  OpenCV version    : {cv2.__version__}")
    print("=" * 60)

    if not validate_paths():
        sys.exit(1)

    cap = open_video(INPUT_VIDEO_PATH)
    fps, total_frames, width, height = print_video_info(cap, INPUT_VIDEO_PATH)
    writer = create_video_writer(OUTPUT_VIDEO_PATH, fps, width, height)

    print("[INFO] Loading MediaPipe PoseLandmarker model (num_poses=5)...")
    base_options = BaseOptions(model_asset_path=MODEL_PATH)
    options = PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=RunningMode.IMAGE,
        num_poses=5,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    with PoseLandmarker.create_from_options(options) as pose_landmarker:
        print("[INFO] Model loaded. Starting target bowler detection...\n")
        frames_processed, total_candidates, target_detected_count, target_lost_count = process_video(
            cap, writer, total_frames, pose_landmarker
        )

    cap.release()
    writer.release()
    cv2.destroyAllWindows()

    target_detection_rate = (target_detected_count / frames_processed * 100) if frames_processed > 0 else 0
    avg_candidates = (total_candidates / frames_processed) if frames_processed > 0 else 0

    print("\n" + "=" * 60)
    print("  CrickSense -- Processing Complete (Target Person Selection)")
    print("=" * 60)
    print(f"  Total frames processed            : {frames_processed}")
    print(f"  Total candidate poses detected    : {total_candidates} (avg {avg_candidates:.2f} per frame)")
    print(f"  Frames with target bowler selected: {target_detected_count} ({target_detection_rate:.1f}%)")
    print(f"  Frames with target bowler lost    : {target_lost_count}")
    print(f"  Output video saved to             : {OUTPUT_VIDEO_PATH}")
    print("=" * 60 + "\n")
    print("[SUCCESS] Target bowler pose selection test complete!\n")


if __name__ == "__main__":
    main()
