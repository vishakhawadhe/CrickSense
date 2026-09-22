"""
=============================================================================
CrickSense -- Data Quality Audit
=============================================================================
Reads all 19 landmark CSV files across General / U15 / U19,
runs quality checks, and writes:
  ai/data/quality_report.csv
  ai/data/quality_report.md

No source data is modified or deleted.
=============================================================================
"""

import os
import csv
import math

BASE_DIR = os.path.dirname(__file__)
LANDMARKS_DIR = os.path.join(BASE_DIR, "data", "landmarks")
DATA_DIR = os.path.join(BASE_DIR, "data")
CATEGORIES = ["General", "U15", "U19"]
NUM_LANDMARKS = 33
FIELDS_PER_LM = 4   # x, y, z, visibility
LM_COL_COUNT = NUM_LANDMARKS * FIELDS_PER_LM  # 132


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def is_invalid(val):
    """Return True if val is empty, non-numeric, NaN or Inf."""
    if val is None or str(val).strip() == "":
        return True
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return True
        return False
    except (ValueError, TypeError):
        return True


def longest_consecutive(seq):
    """Given a list of booleans (True = lost), return longest True run."""
    max_run = 0
    current = 0
    for v in seq:
        if v:
            current += 1
            if current > max_run:
                max_run = current
        else:
            current = 0
    return max_run


def is_intermittent(lost_flags):
    """
    Return True if lost frames are scattered (not all in one block).
    Defines as: number of separate lost-runs > 1
    """
    runs = 0
    in_run = False
    for v in lost_flags:
        if v and not in_run:
            runs += 1
            in_run = True
        elif not v:
            in_run = False
    return runs > 1


def quality_label(pct):
    if pct >= 90:
        return "GOOD"
    elif pct >= 75:
        return "ACCEPTABLE"
    elif pct >= 50:
        return "REVIEW"
    else:
        return "POOR"


# ---------------------------------------------------------------------------
# analyse a single CSV
# ---------------------------------------------------------------------------

def audit_csv(csv_path, category, video_id):
    result = {
        "category": category,
        "video_id": video_id,
        "total_frames": 0,
        "detected_frames": 0,
        "lost_frames": 0,
        "detection_percentage": 0.0,
        "missing_landmark_frames": 0,
        "invalid_value_frames": 0,
        "longest_lost_sequence": 0,
        "quality_status": "POOR",
        # extra detail for md report
        "lost_continuous": False,
        "lost_intermittent": False,
        "detected_complete": True,
        "partial_detected_frames": 0,
    }

    lost_flags = []

    if not os.path.exists(csv_path):
        print(f"  [WARN] Not found: {csv_path}")
        return result

    with open(csv_path, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return result

        for row in reader:
            if not row:
                continue

            result["total_frames"] += 1

            if len(row) < 3:
                result["lost_frames"] += 1
                lost_flags.append(True)
                continue

            target_det = row[2].strip()
            lm_data = row[3:]   # all landmark columns

            if target_det == "0":
                result["lost_frames"] += 1
                lost_flags.append(True)
                # verify missing landmarks (should all be empty)
                result["missing_landmark_frames"] += 1

            elif target_det == "1":
                result["detected_frames"] += 1
                lost_flags.append(False)

                # check for invalid values in landmark data
                has_invalid = False
                has_partial = False

                if len(lm_data) < LM_COL_COUNT:
                    has_partial = True
                    has_invalid = True
                else:
                    for v in lm_data[:LM_COL_COUNT]:
                        if is_invalid(v):
                            has_invalid = True
                            break

                if has_invalid:
                    result["invalid_value_frames"] += 1
                    result["detected_complete"] = False

                if has_partial:
                    result["partial_detected_frames"] += 1

            else:
                # unexpected value
                result["lost_frames"] += 1
                lost_flags.append(True)

    tf = result["total_frames"]
    df = result["detected_frames"]
    result["detection_percentage"] = round((df / tf * 100) if tf > 0 else 0.0, 2)
    result["longest_lost_sequence"] = longest_consecutive(lost_flags)

    num_lost_runs = sum(
        1 for i, v in enumerate(lost_flags)
        if v and (i == 0 or not lost_flags[i - 1])
    )
    result["lost_continuous"] = result["lost_frames"] > 0 and num_lost_runs == 1
    result["lost_intermittent"] = num_lost_runs > 1

    result["quality_status"] = quality_label(result["detection_percentage"])
    return result


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    all_results = []

    print("=" * 70)
    print("  CrickSense -- Data Quality Audit")
    print("=" * 70)

    for category in CATEGORIES:
        cat_dir = os.path.join(LANDMARKS_DIR, category)
        csv_files = sorted([f for f in os.listdir(cat_dir) if f.endswith(".csv")])
        print(f"\nCategory: {category}  ({len(csv_files)} files)")

        for fname in csv_files:
            video_id = fname.replace("_landmarks.csv", "")
            csv_path = os.path.join(cat_dir, fname)
            print(f"  Auditing {fname}...")
            r = audit_csv(csv_path, category, video_id)
            all_results.append(r)
            print(f"    Frames={r['total_frames']}, Detected={r['detected_frames']}, "
                  f"Lost={r['lost_frames']}, {r['detection_percentage']:.2f}% -> {r['quality_status']}")

    # -----------------------------------------------------------------------
    # write quality_report.csv
    # -----------------------------------------------------------------------
    csv_report_path = os.path.join(DATA_DIR, "quality_report.csv")
    csv_cols = [
        "category", "video_id", "total_frames", "detected_frames",
        "lost_frames", "detection_percentage", "missing_landmark_frames",
        "invalid_value_frames", "longest_lost_sequence", "quality_status"
    ]

    with open(csv_report_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=csv_cols)
        w.writeheader()
        for r in all_results:
            w.writerow({k: r[k] for k in csv_cols})

    print(f"\n[OK] CSV report written: {csv_report_path}")

    # -----------------------------------------------------------------------
    # write quality_report.md
    # -----------------------------------------------------------------------
    md_path = os.path.join(DATA_DIR, "quality_report.md")

    total_videos = len(all_results)
    total_frames = sum(r["total_frames"] for r in all_results)
    total_detected = sum(r["detected_frames"] for r in all_results)
    total_lost = sum(r["lost_frames"] for r in all_results)
    avg_det_pct = (total_detected / total_frames * 100) if total_frames > 0 else 0

    good       = [r for r in all_results if r["quality_status"] == "GOOD"]
    acceptable = [r for r in all_results if r["quality_status"] == "ACCEPTABLE"]
    review     = [r for r in all_results if r["quality_status"] == "REVIEW"]
    poor       = [r for r in all_results if r["quality_status"] == "POOR"]

    with open(md_path, "w") as md:

        md.write("# CrickSense -- Data Quality Report\n\n")

        # -------- overall stats --------
        md.write("## Overall Statistics\n\n")
        md.write(f"| Metric | Value |\n|---|---|\n")
        md.write(f"| Total Videos | {total_videos} |\n")
        md.write(f"| Total Frames | {total_frames} |\n")
        md.write(f"| Total Detected Frames | {total_detected} |\n")
        md.write(f"| Total Lost Frames | {total_lost} |\n")
        md.write(f"| Average Detection % | {avg_det_pct:.2f}% |\n")
        md.write(f"| GOOD (>=90%) | {len(good)} |\n")
        md.write(f"| ACCEPTABLE (>=75%) | {len(acceptable)} |\n")
        md.write(f"| REVIEW (>=50%) | {len(review)} |\n")
        md.write(f"| POOR (<50%) | {len(poor)} |\n\n")

        # -------- category-wise --------
        md.write("## Category-wise Statistics\n\n")
        for category in CATEGORIES:
            cat_res = [r for r in all_results if r["category"] == category]
            cf = sum(r["total_frames"] for r in cat_res)
            cd = sum(r["detected_frames"] for r in cat_res)
            cl = sum(r["lost_frames"] for r in cat_res)
            cp = (cd / cf * 100) if cf > 0 else 0
            md.write(f"### {category}\n\n")
            md.write(f"| Metric | Value |\n|---|---|\n")
            md.write(f"| Videos | {len(cat_res)} |\n")
            md.write(f"| Total Frames | {cf} |\n")
            md.write(f"| Detected | {cd} |\n")
            md.write(f"| Lost | {cl} |\n")
            md.write(f"| Avg Detection % | {cp:.2f}% |\n\n")

        # -------- video-wise results --------
        md.write("## Video-wise Results\n\n")
        md.write("| Category | Video | Frames | Detected | Lost | Det % | Longest Lost Seq | Invalid Frames | Status |\n")
        md.write("|---|---|---|---|---|---|---|---|---|\n")
        for r in all_results:
            md.write(
                f"| {r['category']} | {r['video_id']} | {r['total_frames']} | "
                f"{r['detected_frames']} | {r['lost_frames']} | "
                f"{r['detection_percentage']:.2f}% | {r['longest_lost_sequence']} | "
                f"{r['invalid_value_frames']} | {r['quality_status']} |\n"
            )
        md.write("\n")

        # -------- quality lists --------
        def list_section(title, items, md):
            md.write(f"## {title}\n\n")
            if not items:
                md.write("_None_\n\n")
                return
            for r in items:
                md.write(f"- **{r['video_id']}** ({r['category']}) — "
                         f"{r['detection_percentage']:.2f}%, "
                         f"{r['detected_frames']} detected / {r['total_frames']} total\n")
            md.write("\n")

        list_section("GOOD Videos (Detection >= 90%)", good, md)
        list_section("ACCEPTABLE Videos (Detection >= 75%)", acceptable, md)
        list_section("REVIEW Videos (Detection >= 50% < 75%)", review, md)
        list_section("POOR Videos (Detection < 50%)", poor, md)

        # -------- detailed POOR / REVIEW --------
        flagged = review + poor
        if flagged:
            md.write("## Detailed Report: REVIEW and POOR Videos\n\n")
            for r in flagged:
                md.write(f"### {r['video_id']} ({r['category']}) — {r['quality_status']}\n\n")
                md.write(f"| Field | Value |\n|---|---|\n")
                md.write(f"| Filename | {r['video_id']}_landmarks.csv |\n")
                md.write(f"| Detection % | {r['detection_percentage']:.2f}% |\n")
                md.write(f"| Lost Frames | {r['lost_frames']} |\n")
                md.write(f"| Longest Consecutive Lost Sequence | {r['longest_lost_sequence']} frames |\n")
                loss_pattern = "Continuous (one block)" if r["lost_continuous"] else ("Intermittent (scattered)" if r["lost_intermittent"] else "N/A")
                md.write(f"| Loss Pattern | {loss_pattern} |\n")
                detected_complete = "Yes — all detected frames have full 33-landmark data" if r["detected_complete"] else f"No — {r['invalid_value_frames']} detected frames have invalid/partial landmarks"
                md.write(f"| Detected Frames Complete | {detected_complete} |\n")
                md.write("\n")

        # -------- warnings --------
        md.write("## Warnings\n\n")
        high_missing = [r for r in all_results if r["missing_landmark_frames"] / r["total_frames"] * 100 > 30 if r["total_frames"] > 0]
        if high_missing:
            for r in high_missing:
                pct = r["missing_landmark_frames"] / r["total_frames"] * 100
                md.write(f"> **WARNING**: `{r['video_id']}` ({r['category']}) has **{pct:.1f}% missing frames**. "
                         f"This video may not be suitable for training without re-recording or augmentation.\n\n")
        else:
            md.write("_No videos with critically high missing-frame percentages detected._\n\n")

        md.write("---\n_Report generated by CrickSense Data Quality Audit._\n")

    print(f"[OK] Markdown report written: {md_path}")

    # -----------------------------------------------------------------------
    # console summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  QUALITY REPORT SUMMARY")
    print("=" * 70)
    print(f"  Total videos audited   : {total_videos}")
    print(f"  Total frames           : {total_frames}")
    print(f"  Total detected         : {total_detected}")
    print(f"  Total lost             : {total_lost}")
    print(f"  Average detection %    : {avg_det_pct:.2f}%")
    print(f"  GOOD       (>=90%)     : {len(good)}")
    print(f"  ACCEPTABLE (>=75%)     : {len(acceptable)}")
    print(f"  REVIEW     (>=50%)     : {len(review)}")
    print(f"  POOR       (<50%)      : {len(poor)}")

    for label, group in [("GOOD", good), ("ACCEPTABLE", acceptable), ("REVIEW", review), ("POOR", poor)]:
        if group:
            names = ", ".join(r["video_id"] for r in group)
            print(f"\n  {label}:")
            for r in group:
                print(f"    {r['video_id']:20s} ({r['category']:8s})  {r['detection_percentage']:6.2f}%  "
                      f"  lost={r['lost_frames']}  longest_seq={r['longest_lost_sequence']}")

    print(f"\n  Reports saved to:")
    print(f"    {csv_report_path}")
    print(f"    {md_path}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
