#!/usr/bin/env python3
"""Export the CSV/JSON source of truth to Excel.

Usage:
  python scripts/export_excel.py services/<service>                      -> techdebt.xlsx
  python scripts/export_excel.py services/<service>/reviews/<review-dir> -> tracker.xlsx
  python scripts/export_excel.py --all                                   -> everything under services/

Excel files are outputs. Do not edit them by hand; edit the CSV and re-run.
"""
import argparse
import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

NAVY = "1F4E79"
BLUE = "2E75B6"
FONT = "Arial"
MAX_ROW = 2000  # formula ranges cover rows 2..MAX_ROW

STATUSES = ["Open", "Partially fixed", "Fixed (verified)", "Obsolete", "Won't fix"]
OPEN_STATUSES = ["Open", "Partially fixed"]
SEVERITIES = ["BLOCKER", "MAJOR", "MINOR", "QUESTION"]
DEBT_CLASSES = ["Debt-Track", "Debt-Opportunistic"]
TRACKER_CLASSES = ["Fix now", "Debt-Track", "Debt-Opportunistic"]
ORIGINS = ["New", "Existing-touched", "Existing-untouched"]

THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD_FILL = PatternFill("solid", fgColor=NAVY)
SUB_FILL = PatternFill("solid", fgColor=BLUE)
BODY_FONT = Font(name=FONT, size=10)
BOLD_FONT = Font(name=FONT, size=10, bold=True)
HEAD_FONT = Font(name=FONT, size=10, bold=True, color="FFFFFF")
TITLE_FONT = Font(name=FONT, size=14, bold=True, color=NAVY)
WRAP_TOP = Alignment(wrap_text=True, vertical="top")

SEV_FILLS = {"BLOCKER": "F4B6B6", "MAJOR": "F8CBAD", "MINOR": "FFF2CC", "QUESTION": "DDEBF7"}
STATUS_FILLS = {
    "Open": "F8CBAD",
    "Partially fixed": "FFF2CC",
    "Fixed (verified)": "C6E0B4",
    "Obsolete": "D9D9D9",
    "Won't fix": "D9D9D9",
}


# ---------- reading helpers ----------

def read_csv(path: Path):
    if not path.exists():
        return []
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        for n, row in enumerate(csv.DictReader(f), start=2):
            # Extra fields (restkey None) or missing fields (None value) mean an unquoted comma or a short row.
            if None in row or any(v is None for v in row.values()):
                raise SystemExit(
                    f"{path}: line {n} has the wrong number of fields. "
                    "Quote any field that contains a comma, e.g. \"index (status, created_at)\"."
                )
            rows.append({k: v.strip() for k, v in row.items()})
    return rows


def read_profile(path: Path):
    """Parse the simple `key: value` front matter of service-profile.md."""
    out = {}
    if not path.exists():
        return out
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return out
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, val = line.split(":", 1)
            out[key.strip()] = val.split("#", 1)[0].strip()
    return out


def to_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return s  # keep text if it is not an ISO date


def to_int(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return s or None


# ---------- writing helpers ----------

def style_header(ws, ncols, row=1):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = HEAD_FONT
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = BORDER


def write_table(ws, columns, rows, formulas=None):
    """columns: list of dict(key, header, width, kind). formulas: {key: fn(row_idx, letters)->str}"""
    formulas = formulas or {}
    letters = {c["key"]: get_column_letter(i) for i, c in enumerate(columns, 1)}
    for i, c in enumerate(columns, 1):
        ws.cell(row=1, column=i, value=c["header"])
        ws.column_dimensions[get_column_letter(i)].width = c["width"]
    style_header(ws, len(columns))
    ws.row_dimensions[1].height = 32
    for r, row in enumerate(rows, 2):
        for i, c in enumerate(columns, 1):
            key = c["key"]
            if key in formulas:
                value = formulas[key](r, letters)
            elif c.get("kind") == "date":
                value = to_date(row.get(key, ""))
            elif c.get("kind") == "int":
                value = to_int(row.get(key, ""))
            else:
                value = row.get(key, "") or None
            cell = ws.cell(row=r, column=i, value=value)
            cell.font = BODY_FONT
            cell.alignment = WRAP_TOP
            cell.border = BORDER
            if c.get("kind") == "date":
                cell.number_format = "yyyy-mm-dd"
    ws.freeze_panes = "A2"
    last = max(len(rows) + 1, 2)
    ws.auto_filter.ref = f"A1:{get_column_letter(len(columns))}{last}"
    return letters


def add_color_rules(ws, col_letter, mapping):
    rng = f"{col_letter}2:{col_letter}{MAX_ROW}"
    for text, color in mapping.items():
        ws.conditional_formatting.add(
            rng,
            CellIsRule(operator="equal", formula=[f'"{text}"'], fill=PatternFill("solid", bgColor=color, fgColor=color)),
        )


def add_dropdown(ws, col_letter, values):
    dv = DataValidation(type="list", formula1='"' + ",".join(values) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{col_letter}2:{col_letter}{MAX_ROW}")


def put(ws, ref, value, font=BODY_FONT, fill=None, border=True, wrap=True):
    cell = ws[ref]
    cell.value = value
    cell.font = font
    cell.alignment = Alignment(wrap_text=wrap, vertical="center")
    if fill:
        cell.fill = fill
    if border:
        cell.border = BORDER
    return cell


def header_row(ws, row, labels, start_col=1, fill=HEAD_FILL):
    for i, label in enumerate(labels):
        cell = ws.cell(row=row, column=start_col + i, value=label)
        cell.font = HEAD_FONT
        cell.fill = fill
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = BORDER


def rng(sheet, letter):
    return f"{sheet}!${letter}$2:${letter}${MAX_ROW}"


# ---------- register (techdebt.xlsx) ----------

REGISTER_COLS = [
    {"key": "id", "header": "ID", "width": 18},
    {"key": "severity", "header": "Mức độ", "width": 12},
    {"key": "category", "header": "Nhóm rủi ro", "width": 15},
    {"key": "class", "header": "Phân loại", "width": 19},
    {"key": "issue", "header": "Vấn đề", "width": 42},
    {"key": "location", "header": "File / vị trí", "width": 38},
    {"key": "description", "header": "Mô tả", "width": 60},
    {"key": "suggested_fix", "header": "Đề xuất sửa", "width": 52},
    {"key": "status", "header": "Trạng thái", "width": 17},
    {"key": "first_seen", "header": "Lần đầu thấy", "width": 14, "kind": "date"},
    {"key": "first_seen_mr", "header": "MR đầu tiên", "width": 14},
    {"key": "last_checked", "header": "Kiểm tra gần nhất", "width": 16, "kind": "date"},
    {"key": "last_checked_mr", "header": "MR kiểm tra gần nhất", "width": 18},
    {"key": "age", "header": "Tuổi (ngày)", "width": 12},
    {"key": "times_seen", "header": "Số lần review thấy", "width": 14, "kind": "int"},
    {"key": "touched_not_fixed", "header": "Số MR chạm file mà chưa sửa", "width": 18, "kind": "int"},
    {"key": "stale", "header": "Tồn đọng?", "width": 12},
    {"key": "deferred", "header": "Hoãn?", "width": 9},
    {"key": "deferral_reason", "header": "Lý do hoãn", "width": 32},
    {"key": "mitigation", "header": "Giảm thiểu rủi ro tạm thời", "width": 34},
    {"key": "approved_by", "header": "Người duyệt", "width": 16},
    {"key": "target_sprint", "header": "Sprint mục tiêu", "width": 14},
    {"key": "evidence", "header": "Bằng chứng", "width": 50},
]

BACKLOG_KEYS = ["id", "severity", "class", "issue", "location", "first_seen", "age",
                "times_seen", "touched_not_fixed", "last_checked", "status", "evidence"]

HISTORY_COLS = [
    {"key": "date", "header": "Ngày", "width": 13, "kind": "date"},
    {"key": "mr", "header": "MR / nguồn", "width": 18},
    {"key": "debt_id", "header": "Mã nợ", "width": 18},
    {"key": "old_status", "header": "Trạng thái cũ", "width": 18},
    {"key": "new_status", "header": "Trạng thái mới", "width": 18},
    {"key": "evidence", "header": "Bằng chứng", "width": 70},
]


def age_formula(r, L):
    f = L["first_seen"]
    return f'=IF({f}{r}="","",TODAY()-{f}{r})'


def build_register(svc_dir: Path):
    rows = read_csv(svc_dir / "techdebt.csv")
    history = read_csv(svc_dir / "history.csv")
    profile = read_profile(svc_dir / "service-profile.md")
    thr_raw = profile.get("stale_after_days", "")
    thr = int(thr_raw) if thr_raw.isdigit() else None

    def sort_key(r):
        return (r.get("status") not in OPEN_STATUSES, r.get("first_seen") or "9999-99-99", r.get("id", ""))

    rows.sort(key=sort_key)
    cols = [c for c in REGISTER_COLS if thr is not None or c["key"] != "stale"]

    wb = Workbook()
    ws_sum = wb.active
    ws_sum.title = "Summary"
    ws_reg = wb.create_sheet("Register")
    ws_back = wb.create_sheet("Backlog")
    ws_hist = wb.create_sheet("History")

    formulas = {"age": age_formula}
    if thr is not None:
        formulas["stale"] = lambda r, L: (
            f'=IF(AND(OR({L["status"]}{r}="Open",{L["status"]}{r}="Partially fixed"),'
            f'ISNUMBER({L["age"]}{r})),IF({L["age"]}{r}>Summary!$B$3,"STALE",""),"")'
        )
    L = write_table(ws_reg, cols, rows, formulas)
    add_color_rules(ws_reg, L["status"], STATUS_FILLS)
    add_color_rules(ws_reg, L["severity"], SEV_FILLS)
    add_dropdown(ws_reg, L["status"], STATUSES)

    # Backlog: everything not closed, oldest first (snapshot at export time)
    backlog_rows = [r for r in rows if r.get("status") in OPEN_STATUSES]
    bcols = [next(c for c in REGISTER_COLS if c["key"] == k) for k in BACKLOG_KEYS]
    BL = write_table(ws_back, bcols, backlog_rows, {"age": age_formula})
    add_color_rules(ws_back, BL["status"], STATUS_FILLS)
    add_color_rules(ws_back, BL["severity"], SEV_FILLS)

    write_table(ws_hist, HISTORY_COLS, history)

    # Summary
    service = profile.get("service") or svc_dir.name
    ws_sum.column_dimensions["A"].width = 44
    for col in "BCDEFG":
        ws_sum.column_dimensions[col].width = 16
    put(ws_sum, "A1", f"Tổng hợp nợ kỹ thuật – {service}", font=TITLE_FONT, border=False)
    put(ws_sum, "A2", "File xuất tự động từ techdebt.csv. Không sửa tay; thay đổi qua Git / Claude.",
        font=Font(name=FONT, size=9, italic=True), border=False)
    put(ws_sum, "A3", "Ngưỡng tồn đọng (ngày) – lấy từ service-profile.md", font=BOLD_FONT)
    put(ws_sum, "B3", thr if thr is not None else "Không đặt")

    status_rng, sev_rng, class_rng = rng("Register", L["status"]), rng("Register", L["severity"]), rng("Register", L["class"])
    age_rng, tnf_rng = rng("Register", L["age"]), rng("Register", L["touched_not_fixed"])

    header_row(ws_sum, 5, ["Trạng thái"] + SEVERITIES + ["Tổng"])
    for i, st in enumerate(STATUSES, 6):
        put(ws_sum, f"A{i}", st, font=BOLD_FONT)
        for j, sev in enumerate(SEVERITIES):
            col = get_column_letter(2 + j)
            put(ws_sum, f"{col}{i}", f'=COUNTIFS({status_rng},$A{i},{sev_rng},{col}$5)')
        put(ws_sum, f"F{i}", f"=SUM(B{i}:E{i})", font=BOLD_FONT)
    tot = 6 + len(STATUSES)
    put(ws_sum, f"A{tot}", "Tổng", font=BOLD_FONT)
    for col in "BCDEF":
        put(ws_sum, f"{col}{tot}", f"=SUM({col}6:{col}{tot - 1})", font=BOLD_FONT)

    r0 = tot + 2
    header_row(ws_sum, r0, ["Phân loại"] + STATUSES + ["Tổng"], fill=SUB_FILL)
    for i, cl in enumerate(DEBT_CLASSES, r0 + 1):
        put(ws_sum, f"A{i}", cl, font=BOLD_FONT)
        for j, _ in enumerate(STATUSES):
            col = get_column_letter(2 + j)
            put(ws_sum, f"{col}{i}", f'=COUNTIFS({class_rng},$A{i},{status_rng},{col}${r0})')
        put(ws_sum, f"G{i}", f"=SUM(B{i}:F{i})", font=BOLD_FONT)

    m0 = r0 + len(DEBT_CLASSES) + 2
    header_row(ws_sum, m0, ["Chỉ số nợ còn mở", "Giá trị"], fill=SUB_FILL)
    open_cnt = "+".join(f'COUNTIF({status_rng},"{s}")' for s in OPEN_STATUSES)
    tnf_sum = "+".join(f'SUMIFS({tnf_rng},{status_rng},"{s}")' for s in OPEN_STATUSES)
    oldest = ",".join(f'_xlfn.MAXIFS({age_rng},{status_rng},"{s}")' for s in OPEN_STATUSES)
    metrics = [
        ("Số mục còn mở (Open + Partially fixed)", f"={open_cnt}"),
        ("Tuổi lớn nhất của mục còn mở (ngày)", f"=MAX({oldest})"),
        ("Tổng số lần MR chạm file mà chưa sửa (mục còn mở)", f"={tnf_sum}"),
    ]
    if thr is not None:
        metrics.append(("Số mục tồn đọng (STALE)", f'=COUNTIF({rng("Register", L["stale"])},"STALE")'))
    for i, (label, formula) in enumerate(metrics, m0 + 1):
        put(ws_sum, f"A{i}", label, font=BOLD_FONT)
        put(ws_sum, f"B{i}", formula)
    ws_sum.freeze_panes = "A5"

    wb.calculation.fullCalcOnLoad = True
    out = svc_dir / "techdebt.xlsx"
    wb.save(out)
    return out


# ---------- tracker (per MR) ----------

FINDING_COLS = [
    {"key": "id", "header": "ID", "width": 8},
    {"key": "severity", "header": "Mức độ", "width": 12},
    {"key": "origin", "header": "Nguồn gốc", "width": 19},
    {"key": "part", "header": "Nhóm", "width": 26},
    {"key": "issue", "header": "Vấn đề", "width": 42},
    {"key": "location", "header": "File / vị trí", "width": 38},
    {"key": "description", "header": "Mô tả", "width": 60},
    {"key": "suggested_fix", "header": "Đề xuất sửa", "width": 52},
    {"key": "class", "header": "Phân loại", "width": 19},
    {"key": "debt_id", "header": "Mã nợ", "width": 18},
    {"key": "note", "header": "Ghi chú của reviewer", "width": 40},
]

DEBTCHECK_COLS = [
    {"key": "debt_id", "header": "Mã nợ", "width": 18},
    {"key": "issue", "header": "Vấn đề", "width": 46},
    {"key": "previous_status", "header": "Trạng thái trước", "width": 18},
    {"key": "result", "header": "Kết quả trong MR này", "width": 26},
    {"key": "new_status", "header": "Trạng thái mới", "width": 18},
    {"key": "evidence", "header": "Bằng chứng", "width": 60},
]


def build_tracker(review_dir: Path):
    findings = read_csv(review_dir / "findings.csv")
    checks = read_csv(review_dir / "debt_check.csv")
    meta_path = review_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

    wb = Workbook()
    ws_sum = wb.active
    ws_sum.title = "Summary"
    ws_f = wb.create_sheet("Findings")
    ws_c = wb.create_sheet("DebtCheck")

    L = write_table(ws_f, FINDING_COLS, findings)
    add_color_rules(ws_f, L["severity"], SEV_FILLS)
    CL = write_table(ws_c, DEBTCHECK_COLS, checks)
    add_color_rules(ws_c, CL["new_status"], STATUS_FILLS)
    add_color_rules(ws_c, CL["previous_status"], STATUS_FILLS)

    ws_sum.column_dimensions["A"].width = 34
    for col in "BCDE":
        ws_sum.column_dimensions[col].width = 22
    title = f"Review {meta.get('mr', '')} – {meta.get('service', review_dir.parent.parent.name)}".strip()
    put(ws_sum, "A1", title, font=TITLE_FONT, border=False)
    header_row(ws_sum, 3, ["Thông tin", "Giá trị"])
    info = [
        ("Service", meta.get("service", "")),
        ("MR", meta.get("mr", "")),
        ("Ngày review", meta.get("date", "")),
        ("Nhóm rủi ro", meta.get("risk_tier", "")),
        ("Reviewer", meta.get("reviewer", "")),
        ("Khuyến nghị (chỉ mang tính tham khảo)", meta.get("verdict", "")),
        ("Lý do", meta.get("verdict_reason", "")),
    ]
    for i, (k, v) in enumerate(info, 4):
        put(ws_sum, f"A{i}", k, font=BOLD_FONT)
        put(ws_sum, f"B{i}", v)
        ws_sum.merge_cells(f"B{i}:E{i}")

    sev_rng, cls_rng, org_rng = rng("Findings", L["severity"]), rng("Findings", L["class"]), rng("Findings", L["origin"])
    r0 = 4 + len(info) + 1
    header_row(ws_sum, r0, ["Mức độ × Phân loại"] + TRACKER_CLASSES + ["Tổng"])
    for i, sev in enumerate(SEVERITIES, r0 + 1):
        put(ws_sum, f"A{i}", sev, font=BOLD_FONT)
        for j in range(len(TRACKER_CLASSES)):
            col = get_column_letter(2 + j)
            put(ws_sum, f"{col}{i}", f'=COUNTIFS({sev_rng},$A{i},{cls_rng},{col}${r0})')
        put(ws_sum, f"E{i}", f"=SUM(B{i}:D{i})", font=BOLD_FONT)
    tot = r0 + len(SEVERITIES) + 1
    put(ws_sum, f"A{tot}", "Tổng", font=BOLD_FONT)
    for col in "BCDE":
        put(ws_sum, f"{col}{tot}", f"=SUM({col}{r0 + 1}:{col}{tot - 1})", font=BOLD_FONT)

    o0 = tot + 2
    header_row(ws_sum, o0, ["Mức độ × Nguồn gốc"] + ORIGINS + ["Tổng"], fill=SUB_FILL)
    for i, sev in enumerate(SEVERITIES, o0 + 1):
        put(ws_sum, f"A{i}", sev, font=BOLD_FONT)
        for j in range(len(ORIGINS)):
            col = get_column_letter(2 + j)
            put(ws_sum, f"{col}{i}", f'=COUNTIFS({sev_rng},$A{i},{org_rng},{col}${o0})')
        put(ws_sum, f"E{i}", f"=SUM(B{i}:D{i})", font=BOLD_FONT)

    ws_sum.freeze_panes = "A4"
    wb.calculation.fullCalcOnLoad = True
    out = review_dir / "tracker.xlsx"
    wb.save(out)
    return out


# ---------- entry ----------

def export_dir(path: Path):
    if (path / "techdebt.csv").exists():
        return build_register(path)
    if (path / "findings.csv").exists():
        return build_tracker(path)
    raise SystemExit(f"{path}: no techdebt.csv or findings.csv found")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", nargs="?", help="service folder or review folder")
    ap.add_argument("--all", action="store_true", help="export every service and review under services/")
    args = ap.parse_args()

    if args.all:
        root = Path(__file__).resolve().parent.parent / "services"
        targets = []
        for svc in sorted(p for p in root.iterdir() if p.is_dir()):
            if (svc / "techdebt.csv").exists():
                targets.append(svc)
            targets += sorted(p.parent for p in (svc / "reviews").glob("*/findings.csv"))
    elif args.dir:
        targets = [Path(args.dir)]
    else:
        ap.error("give a folder or --all")

    for t in targets:
        print("wrote", export_dir(t))


if __name__ == "__main__":
    sys.exit(main())
