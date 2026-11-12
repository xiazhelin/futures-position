"""用钢联导出的 Excel 初始化/覆盖历史数据（一次性）。
用法: python scripts/seed_from_xlsx.py data/seed_mysteel.xlsx
列顺序须为: 日期, RU, NR, BR, RB, HC, JM, J, I
"""
import sys, datetime, openpyxl
from common import VARIETIES, save

codes = list(VARIETIES)
ws = openpyxl.load_workbook(sys.argv[1], data_only=True).active
dates, series = [], {c: [] for c in codes}
for row in ws.iter_rows(values_only=True):
    if not isinstance(row[0], datetime.datetime):
        continue
    vals = [v if isinstance(v, (int, float)) else None for v in row[1:1 + len(codes)]]
    if all(v is None for v in vals):
        continue
    dates.append(row[0].strftime("%Y-%m-%d"))
    for c, v in zip(codes, vals):
        series[c].append(int(v) if v is not None else None)
save({"updated": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M"), "dates": dates, "series": series})
print(f"seeded {len(dates)} days: {dates[0]} ~ {dates[-1]}")
