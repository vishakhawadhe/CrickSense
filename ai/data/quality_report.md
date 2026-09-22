# CrickSense -- Data Quality Report

## Overall Statistics

| Metric | Value |
|---|---|
| Total Videos | 19 |
| Total Frames | 4082 |
| Total Detected Frames | 2941 |
| Total Lost Frames | 1141 |
| Average Detection % | 72.05% |
| GOOD (>=90%) | 8 |
| ACCEPTABLE (>=75%) | 3 |
| REVIEW (>=50%) | 5 |
| POOR (<50%) | 3 |

## Category-wise Statistics

### General

| Metric | Value |
|---|---|
| Videos | 7 |
| Total Frames | 1736 |
| Detected | 1019 |
| Lost | 717 |
| Avg Detection % | 58.70% |

### U15

| Metric | Value |
|---|---|
| Videos | 6 |
| Total Frames | 1480 |
| Detected | 1220 |
| Lost | 260 |
| Avg Detection % | 82.43% |

### U19

| Metric | Value |
|---|---|
| Videos | 6 |
| Total Frames | 866 |
| Detected | 702 |
| Lost | 164 |
| Avg Detection % | 81.06% |

## Video-wise Results

| Category | Video | Frames | Detected | Lost | Det % | Longest Lost Seq | Invalid Frames | Status |
|---|---|---|---|---|---|---|---|---|
| General | S_v5 | 50 | 50 | 0 | 100.00% | 0 | 0 | GOOD |
| General | s_v1 | 313 | 176 | 137 | 56.23% | 46 | 0 | REVIEW |
| General | s_v2 | 558 | 381 | 177 | 68.28% | 44 | 0 | REVIEW |
| General | s_v3 | 90 | 89 | 1 | 98.89% | 1 | 0 | GOOD |
| General | s_v4 | 59 | 54 | 5 | 91.53% | 4 | 0 | GOOD |
| General | s_v6 | 558 | 193 | 365 | 34.59% | 138 | 0 | POOR |
| General | s_v7 | 108 | 76 | 32 | 70.37% | 30 | 0 | REVIEW |
| U15 | U15_v1 | 438 | 428 | 10 | 97.72% | 10 | 0 | GOOD |
| U15 | U15_v2 | 306 | 289 | 17 | 94.44% | 3 | 0 | GOOD |
| U15 | U15_v3 | 165 | 163 | 2 | 98.79% | 1 | 0 | GOOD |
| U15 | U15_v4 | 381 | 178 | 203 | 46.72% | 73 | 0 | POOR |
| U15 | U15_v5 | 110 | 82 | 28 | 74.55% | 23 | 0 | REVIEW |
| U15 | U15_v6 | 80 | 80 | 0 | 100.00% | 0 | 0 | GOOD |
| U19 | U19_v1 | 336 | 320 | 16 | 95.24% | 10 | 0 | GOOD |
| U19 | U19_v2 | 62 | 18 | 44 | 29.03% | 43 | 0 | POOR |
| U19 | U19_v3 | 90 | 69 | 21 | 76.67% | 20 | 0 | ACCEPTABLE |
| U19 | U19_v4 | 203 | 157 | 46 | 77.34% | 46 | 0 | ACCEPTABLE |
| U19 | U19_v5 | 110 | 94 | 16 | 85.45% | 3 | 0 | ACCEPTABLE |
| U19 | U19_v6 | 65 | 44 | 21 | 67.69% | 19 | 0 | REVIEW |

## GOOD Videos (Detection >= 90%)

- **S_v5** (General) — 100.00%, 50 detected / 50 total
- **s_v3** (General) — 98.89%, 89 detected / 90 total
- **s_v4** (General) — 91.53%, 54 detected / 59 total
- **U15_v1** (U15) — 97.72%, 428 detected / 438 total
- **U15_v2** (U15) — 94.44%, 289 detected / 306 total
- **U15_v3** (U15) — 98.79%, 163 detected / 165 total
- **U15_v6** (U15) — 100.00%, 80 detected / 80 total
- **U19_v1** (U19) — 95.24%, 320 detected / 336 total

## ACCEPTABLE Videos (Detection >= 75%)

- **U19_v3** (U19) — 76.67%, 69 detected / 90 total
- **U19_v4** (U19) — 77.34%, 157 detected / 203 total
- **U19_v5** (U19) — 85.45%, 94 detected / 110 total

## REVIEW Videos (Detection >= 50% < 75%)

- **s_v1** (General) — 56.23%, 176 detected / 313 total
- **s_v2** (General) — 68.28%, 381 detected / 558 total
- **s_v7** (General) — 70.37%, 76 detected / 108 total
- **U15_v5** (U15) — 74.55%, 82 detected / 110 total
- **U19_v6** (U19) — 67.69%, 44 detected / 65 total

## POOR Videos (Detection < 50%)

- **s_v6** (General) — 34.59%, 193 detected / 558 total
- **U15_v4** (U15) — 46.72%, 178 detected / 381 total
- **U19_v2** (U19) — 29.03%, 18 detected / 62 total

## Detailed Report: REVIEW and POOR Videos

### s_v1 (General) — REVIEW

| Field | Value |
|---|---|
| Filename | s_v1_landmarks.csv |
| Detection % | 56.23% |
| Lost Frames | 137 |
| Longest Consecutive Lost Sequence | 46 frames |
| Loss Pattern | Intermittent (scattered) |
| Detected Frames Complete | Yes — all detected frames have full 33-landmark data |

### s_v2 (General) — REVIEW

| Field | Value |
|---|---|
| Filename | s_v2_landmarks.csv |
| Detection % | 68.28% |
| Lost Frames | 177 |
| Longest Consecutive Lost Sequence | 44 frames |
| Loss Pattern | Intermittent (scattered) |
| Detected Frames Complete | Yes — all detected frames have full 33-landmark data |

### s_v7 (General) — REVIEW

| Field | Value |
|---|---|
| Filename | s_v7_landmarks.csv |
| Detection % | 70.37% |
| Lost Frames | 32 |
| Longest Consecutive Lost Sequence | 30 frames |
| Loss Pattern | Intermittent (scattered) |
| Detected Frames Complete | Yes — all detected frames have full 33-landmark data |

### U15_v5 (U15) — REVIEW

| Field | Value |
|---|---|
| Filename | U15_v5_landmarks.csv |
| Detection % | 74.55% |
| Lost Frames | 28 |
| Longest Consecutive Lost Sequence | 23 frames |
| Loss Pattern | Intermittent (scattered) |
| Detected Frames Complete | Yes — all detected frames have full 33-landmark data |

### U19_v6 (U19) — REVIEW

| Field | Value |
|---|---|
| Filename | U19_v6_landmarks.csv |
| Detection % | 67.69% |
| Lost Frames | 21 |
| Longest Consecutive Lost Sequence | 19 frames |
| Loss Pattern | Intermittent (scattered) |
| Detected Frames Complete | Yes — all detected frames have full 33-landmark data |

### s_v6 (General) — POOR

| Field | Value |
|---|---|
| Filename | s_v6_landmarks.csv |
| Detection % | 34.59% |
| Lost Frames | 365 |
| Longest Consecutive Lost Sequence | 138 frames |
| Loss Pattern | Intermittent (scattered) |
| Detected Frames Complete | Yes — all detected frames have full 33-landmark data |

### U15_v4 (U15) — POOR

| Field | Value |
|---|---|
| Filename | U15_v4_landmarks.csv |
| Detection % | 46.72% |
| Lost Frames | 203 |
| Longest Consecutive Lost Sequence | 73 frames |
| Loss Pattern | Intermittent (scattered) |
| Detected Frames Complete | Yes — all detected frames have full 33-landmark data |

### U19_v2 (U19) — POOR

| Field | Value |
|---|---|
| Filename | U19_v2_landmarks.csv |
| Detection % | 29.03% |
| Lost Frames | 44 |
| Longest Consecutive Lost Sequence | 43 frames |
| Loss Pattern | Intermittent (scattered) |
| Detected Frames Complete | Yes — all detected frames have full 33-landmark data |

## Warnings

> **WARNING**: `s_v1` (General) has **43.8% missing frames**. This video may not be suitable for training without re-recording or augmentation.

> **WARNING**: `s_v2` (General) has **31.7% missing frames**. This video may not be suitable for training without re-recording or augmentation.

> **WARNING**: `s_v6` (General) has **65.4% missing frames**. This video may not be suitable for training without re-recording or augmentation.

> **WARNING**: `U15_v4` (U15) has **53.3% missing frames**. This video may not be suitable for training without re-recording or augmentation.

> **WARNING**: `U19_v2` (U19) has **71.0% missing frames**. This video may not be suitable for training without re-recording or augmentation.

> **WARNING**: `U19_v6` (U19) has **32.3% missing frames**. This video may not be suitable for training without re-recording or augmentation.

---
_Report generated by CrickSense Data Quality Audit._
