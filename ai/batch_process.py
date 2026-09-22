import os
import glob
import subprocess
import csv

BASE_DIR = os.path.dirname(__file__)
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
LANDMARKS_DIR = os.path.join(BASE_DIR, "data", "landmarks")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
PYTHON_EXEC = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")
SCRIPT_PATH = os.path.join(BASE_DIR, "pose_detection.py")

CATEGORIES = ["General", "U15", "U19"]

def count_csv_stats(csv_path):
    rows = 0
    detected = 0
    lost = 0
    cols = 0
    with open(csv_path, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header:
            cols = len(header) - 3 # excluding video_id, frame_id, target_detected
        for row in reader:
            if not row: continue
            rows += 1
            if int(row[2]) == 1:
                detected += 1
            else:
                lost += 1
    return rows, detected, lost, cols

def main():
    report = []
    
    total_videos = 0
    total_frames = 0
    total_detected = 0
    total_lost = 0

    print("Starting Batch Processing...")
    
    for category in CATEGORIES:
        print(f"\nProcessing Category: {category}")
        cat_dir = os.path.join(RAW_DIR, category)
        videos = glob.glob(os.path.join(cat_dir, "*.mp4"))
        
        for video_path in videos:
            total_videos += 1
            video_basename = os.path.basename(video_path)
            video_id = os.path.splitext(video_basename)[0]
            csv_path = os.path.join(LANDMARKS_DIR, category, f"{video_id}_landmarks.csv")
            
            if os.path.exists(csv_path):
                print(f"  [SKIP] CSV already exists for {video_basename}")
                try:
                    rows, detected, lost, cols = count_csv_stats(csv_path)
                    report.append({
                        "category": category,
                        "video": video_basename,
                        "frames": rows,
                        "detected": detected,
                        "lost": lost,
                        "detection_pct": (detected / rows * 100) if rows > 0 else 0,
                        "rows": rows,
                        "cols": cols,
                        "csv_path": csv_path,
                        "status": "Skipped (Exists)"
                    })
                    total_frames += rows
                    total_detected += detected
                    total_lost += lost
                except Exception as e:
                    print(f"Error reading existing CSV: {e}")
                continue
            
            output_video = os.path.join(OUTPUT_DIR, f"{video_id}_output.mp4")
            print(f"  [PROCESS] Running on {video_basename}...")
            
            try:
                res = subprocess.run([PYTHON_EXEC, SCRIPT_PATH, video_path, output_video], capture_output=True, text=True)
                if res.returncode != 0:
                    print(f"  [ERROR] Processing failed for {video_basename}")
                    print(res.stderr)
                    report.append({
                        "category": category,
                        "video": video_basename,
                        "status": "Failed"
                    })
                    continue
                
                rows, detected, lost, cols = count_csv_stats(csv_path)
                report.append({
                    "category": category,
                    "video": video_basename,
                    "frames": rows,
                    "detected": detected,
                    "lost": lost,
                    "detection_pct": (detected / rows * 100) if rows > 0 else 0,
                    "rows": rows,
                    "cols": cols,
                    "csv_path": csv_path,
                    "status": "Success"
                })
                total_frames += rows
                total_detected += detected
                total_lost += lost
                
            except Exception as e:
                print(f"  [ERROR] Exception running process for {video_basename}: {e}")
                report.append({
                    "category": category,
                    "video": video_basename,
                    "status": "Failed (Exception)"
                })

    print("\n" + "="*80)
    print("BATCH PROCESSING SUMMARY REPORT")
    print("="*80)
    
    for category in CATEGORIES:
        print(f"\nCategory: {category}")
        cat_reports = [r for r in report if r["category"] == category]
        if not cat_reports:
            print("  No videos found/processed.")
            continue
        
        for r in cat_reports:
            print(f"\n  Video: {r['video']}")
            if "frames" in r:
                print(f"    Total frames       : {r['frames']}")
                print(f"    Target detected    : {r['detected']}")
                print(f"    TARGET LOST        : {r['lost']}")
                print(f"    Detection %        : {r['detection_pct']:.2f}%")
                print(f"    CSV rows           : {r['rows']}")
                print(f"    Landmark columns   : {r['cols']}")
                print(f"    CSV output path    : {r['csv_path']}")
                print(f"    Status             : {r['status']}")
            else:
                print(f"    Status             : {r['status']}")
                
    print("\n" + "="*80)
    print("OVERALL CATEGORY TOTALS")
    print("="*80)
    print(f"  Total Videos               : {total_videos}")
    print(f"  Total Frames               : {total_frames}")
    print(f"  Total Detected Frames      : {total_detected}")
    print(f"  Total Lost Frames          : {total_lost}")
    avg_pct = (total_detected / total_frames * 100) if total_frames > 0 else 0
    print(f"  Average Detection %        : {avg_pct:.2f}%")
    
    success_csvs = [r for r in report if r.get("status") in ["Success", "Skipped (Exists)"]]
    print(f"\n  CSV Files Generated/Found  : {len(success_csvs)}")
    
    # Verifications
    all_132_cols = all(r.get("cols") == 132 for r in success_csvs)
    print(f"  All successful CSVs have 132 landmark cols : {all_132_cols}")
    
    all_rows_match_frames = all(r.get("rows") == r.get("frames") for r in success_csvs)
    print(f"  CSV row count matches frame count          : {all_rows_match_frames}")

if __name__ == "__main__":
    main()
