# CrickSense — Step 1: OpenCV + MediaPipe Pose Detection Test

## Overview
This is **Step 1** of the CrickSense project.  
Goal: Verify that OpenCV can read a bowling video and MediaPipe BlazePose
can detect the cricketer's body pose (33 landmarks) frame-by-frame.

---

## Project Structure

```
CrickSense/
└── ai/
    ├── videos/
    │   └── bowling.mp4         ← Place your bowling video here
    ├── output/
    │   └── output_pose.mp4     ← Processed video will appear here
    ├── pose_detection.py       ← Main script
    ├── requirements.txt        ← Python dependencies
    └── README.md               ← This file
```

---

## Prerequisites

- Python **3.9** or **3.10** (recommended)
- pip

---

## Setup Instructions

### 1. Create a virtual environment

Open a terminal in the `CrickSense/ai/` folder and run:

```bash
python -m venv venv
```

### 2. Activate the virtual environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your bowling video

Copy your bowling video into:
```
CrickSense/ai/videos/bowling.mp4
```

### 5. Run the script

```bash
python pose_detection.py
```

---

## What the Script Does

1. Opens `videos/bowling.mp4` using OpenCV
2. Prints video metadata:
   - FPS
   - Total frames
   - Resolution
   - Duration
3. Passes each frame to MediaPipe BlazePose
4. Detects 33 body landmarks per frame
5. Draws the skeleton overlay on the frame
6. Saves the result to `output/output_pose.mp4`
7. Prints per-frame detection status (landmark count or "Not detected")

---

## Expected Console Output (example)

```
============================================================
  CrickSense -- Video Information
============================================================
  File       : .../videos/bowling.mp4
  FPS        : 30.00
  Frames     : 450
  Resolution : 1920 x 1080 pixels
  Duration   : 15.00 seconds  (0.25 minutes)
============================================================

  Frame   Landmarks  Status
----------------------------------------
      1          33  Detected
      2          33  Detected
      3           0  Not detected
      4          33  Detected
    ...
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `[ERROR] Video file not found` | Ensure `bowling.mp4` is placed in `ai/videos/` |
| `ModuleNotFoundError: mediapipe` | Run `pip install -r requirements.txt` |
| Very slow processing | Normal for CPU — MediaPipe runs on CPU by default |
| All frames show "Not detected" | Video quality may be low; try `min_detection_confidence=0.3` |

---

## Next Steps (not yet implemented)

- Step 2: Extract joint angles from landmarks
- Step 3: ST-GCN for action classification  
- Step 4: Biomechanics analysis
- Step 5: Scoring & injury risk
- Step 6: React dashboard + Node.js + MongoDB
