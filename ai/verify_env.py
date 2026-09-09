"""
CrickSense -- Environment Verification Script
=============================================
Run this with:  .\\venv\\Scripts\\python.exe verify_env.py

This script checks:
  1. Python interpreter path and version
  2. cv2 (OpenCV) import
  3. mediapipe import
  4. MediaPipe PoseLandmarker (Tasks API -- mediapipe >= 1.0.0)
  5. Whether the model file exists
  6. Whether the video file exists
  7. Whether OpenCV can open the video
  8. Whether PoseLandmarker initializes successfully
"""

import sys
import os

PASS = "[  OK  ]"
FAIL = "[ FAIL ]"
SKIP = "[ SKIP ]"

print("\n" + "=" * 57)
print("  CrickSense -- Environment & Import Verification")
print("=" * 57)

# -- 1. Python interpreter ------------------------------------------------
print(f"\n[1] Python interpreter : {sys.executable}")
print(f"    Python version     : {sys.version.split()[0]}")

# -- 2. OpenCV import -----------------------------------------------------
cv2 = None
try:
    import cv2
    print(f"\n[2] {PASS} OpenCV import    : SUCCESS  (cv2 {cv2.__version__})")
    cv2_ok = True
except ImportError as e:
    print(f"\n[2] {FAIL} OpenCV import    : FAILED   ({e})")
    cv2_ok = False

# -- 3. MediaPipe import --------------------------------------------------
mp = None
try:
    import mediapipe as mp
    print(f"[3] {PASS} MediaPipe import : SUCCESS  (mediapipe {mp.__version__})")
    mp_ok = True
except ImportError as e:
    print(f"[3] {FAIL} MediaPipe import : FAILED   ({e})")
    mp_ok = False

# -- 4. MediaPipe Tasks API (PoseLandmarker) ------------------------------
PoseLandmarker = None
PoseLandmarkerOptions = None
RunningMode = None
BaseOptions = None

if mp_ok and mp is not None:
    try:
        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode
        BaseOptions = mp.tasks.BaseOptions
        print(f"[4] {PASS} Tasks API       : SUCCESS  (PoseLandmarker available)")
        tasks_ok = True
    except (ImportError, AttributeError) as e:
        print(f"[4] {FAIL} Tasks API       : FAILED   ({e})")
        tasks_ok = False
else:
    print(f"[4] {SKIP} Tasks API       : SKIPPED  (mediapipe import failed)")
    tasks_ok = False

# -- 5. Model file existence ----------------------------------------------
model_path = os.path.join(os.path.dirname(__file__), "models", "pose_landmarker_full.task")
if os.path.exists(model_path):
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"[5] {PASS} Model file      : FOUND    ({size_mb:.1f} MB)")
    model_found = True
else:
    print(f"[5] {FAIL} Model file      : NOT FOUND")
    print(f"         Expected : {model_path}")
    print("         Run this command to download it:")
    print("         Invoke-WebRequest -Uri 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task' -OutFile ai\\models\\pose_landmarker_full.task -UseBasicParsing")
    model_found = False

# -- 6. Video file existence ----------------------------------------------
video_path = os.path.join(os.path.dirname(__file__), "videos", "bowling_v1.mp4")
if os.path.exists(video_path):
    size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"[6] {PASS} Video file      : FOUND    ({size_mb:.1f} MB)  bowling_v1.mp4")
    video_found = True
else:
    print(f"[6] {FAIL} Video file      : NOT FOUND")
    print(f"         Expected : {video_path}")
    print(f"         Action   : Place your bowling_v1.mp4 in ai/videos/")
    video_found = False

# -- 7. OpenCV video open -------------------------------------------------
if cv2_ok and video_found and cv2 is not None:
    cap = cv2.VideoCapture(video_path)
    if cap.isOpened():
        fps    = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        w      = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        dur    = frames / fps if fps > 0 else 0
        print(f"[7] {PASS} Video opened    : SUCCESS")
        print(f"         FPS={fps:.1f}  Frames={frames}  Resolution={w}x{h}  Duration={dur:.1f}s")
        cap.release()
        video_open_ok = True
    else:
        print(f"[7] {FAIL} Video opened    : FAILED  (OpenCV could not decode the file)")
        video_open_ok = False
else:
    reason = "cv2 import failed" if not cv2_ok else "video file not found"
    print(f"[7] {SKIP} Video opened    : SKIPPED ({reason})")
    video_open_ok = False

# -- 8. PoseLandmarker init -----------------------------------------------
if tasks_ok and model_found and BaseOptions is not None and PoseLandmarkerOptions is not None and RunningMode is not None and PoseLandmarker is not None:
    try:
        base_options = BaseOptions(model_asset_path=model_path)
        options = PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=RunningMode.IMAGE,
            num_poses=1,
        )
        with PoseLandmarker.create_from_options(options) as lm:
            pass  # just loading the model is enough
        print(f"[8] {PASS} Pose detection  : SUCCESS  (PoseLandmarker model loaded)")
        pose_ok = True
    except Exception as e:
        print(f"[8] {FAIL} Pose detection  : FAILED   ({e})")
        pose_ok = False
else:
    reason = "Tasks API failed" if not tasks_ok else "model file not found"
    print(f"[8] {SKIP} Pose detection  : SKIPPED ({reason})")
    pose_ok = False

# -- Summary --------------------------------------------------------------
print("\n" + "=" * 57)
print("  Summary")
print("=" * 57)
print(f"  OpenCV import    : {'SUCCESS'    if cv2_ok       else 'FAILED'}")
print(f"  MediaPipe import : {'SUCCESS'    if mp_ok        else 'FAILED'}")
print(f"  Tasks API        : {'SUCCESS'    if tasks_ok     else 'FAILED'}")
print(f"  Model file       : {'FOUND'      if model_found  else 'NOT FOUND'}")
print(f"  Video file       : {'FOUND'      if video_found  else 'NOT FOUND'}")
print(f"  Video opened     : {'SUCCESS'    if video_open_ok else 'FAILED/SKIPPED'}")
print(f"  Pose detection   : {'SUCCESS'    if pose_ok      else 'FAILED/SKIPPED'}")
print()

env_ready = cv2_ok and mp_ok and tasks_ok and model_found and pose_ok

if env_ready and video_found and video_open_ok:
    print("  ALL CHECKS PASSED -- run:  python pose_detection.py")
elif env_ready and not video_found:
    print("  Environment is READY.")
    print("  Place bowling_v1.mp4 in ai/videos/ then run pose_detection.py")
else:
    print("  Some checks FAILED -- see details above.")
print("=" * 57 + "\n")
