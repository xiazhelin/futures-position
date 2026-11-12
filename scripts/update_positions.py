"""每日增量更新持仓量（仅用 Python 标准库）。
- 上期所/能源中心品种: 交易所官方日行情 kxYYYYMMDD.dat，分合约持仓加总
- 大商所品种: 交易所官网有反爬，改用新浪财经分合约日线的持仓量加总
  （当日无成交的远月合约会缺失，与官方值偏差通常 <1%）
从 positions.json 最后一个日期的次日补到今天，可重复运行。
"""
import datetime, json, re, sys, time, urllib.request, urllib.error
from common import VARIETIES, load, save

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
BJ = datetime.timezone(datetime.timedelta(hours=8))


def get(url, retries=3):
    for i in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            err = e
        except Exception as e:  # noqa
            err = e
        time.sleep(2 * (i + 1))
    raise RuntimeError(f"fetch failed: {url}: {err}")


def shfe_day(day):
    """返回 {源内代码: 总持仓}；非交易日或尚未发布返回 None。"""
    txt = get(f"https://www.shfe.com.cn/data/tradedata/future/dailydata/kx{day:%Y%m%d}.dat")
    if not txt or not txt.lstrip().startswith("{"):
        return None
    out = {}
    for r in json.loads(txt).get("o_curinstrument", []):
        month = str(r.get("DELIVERYMONTH", "")).strip()
        oi = r.get("OPENINTEREST")
        if not month.isdigit() or oi in ("", None):
            continue
        pid = str(r.get("PRODUCTID", "")).strip()
        out[pid] = out.get(pid, 0) + int(oi)
    return out or None


def sina_totals(prefix, today):
    """返回 {日期: 各合约持仓之和}。"""
    totals = {}
    y, m = today.year, today.month
    for k in range(-1, 14):
        yy, mm = y + (m - 1 + k) // 12, (m - 1 + k) % 12 + 1
        sym = f"{prefix}{yy % 100:02d}{mm:02d}"
        txt = get("https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var%20t=/"
                  f"InnerFuturesNewService.getDailyKLine?symbol={sym}")
        mt = re.search(r"\((\[.*\])\)", txt or "", re.S)
        if not mt:
            continue
        for row in json.loads(mt.group(1)):
            totals[row["d"]] = totals.get(row["d"], 0) + int(float(row["p"]))
        time.sleep(0.3)
    return totals


def main():
    d = load()
    now = datetime.datetime.now(BJ)
    today = now.date()
    # 盘中交易所文件是未收盘快照，16:00(北京)前不取当日
    last_ok = today if now.hour >= 16 else today - datetime.timedelta(days=1)
    day = datetime.date.fromisoformat(d["dates"][-1]) + datetime.timedelta(days=1)
    sina = None
    added = 0
    while day <= last_ok:
        if day.weekday() < 5:
            shfe = shfe_day(day)
            if shfe:
                if sina is None:
                    sina = {c: sina_totals(v[3], today) for c, v in VARIETIES.items() if v[2] == "sina"}
                ds = day.isoformat()
                d["dates"].append(ds)
                for c, v in VARIETIES.items():
                    val = shfe.get(v[3]) if v[2] == "shfe" else sina[c].get(ds)
                    d["series"].setdefault(c, [None] * (len(d["dates"]) - 1)).append(val)
                added += 1
                print("added", ds, {c: d["series"][c][-1] for c in VARIETIES})
        day += datetime.timedelta(days=1)
    # 回填最近 5 个交易日里新浪源的空值（当日抓取时新浪尚未更新的情况）
    for c, v in VARIETIES.items():
        if v[2] != "sina":
            continue
        for i in range(max(0, len(d["dates"]) - 5), len(d["dates"])):
            if d["series"][c][i] is None:
                if sina is None:
                    sina = {k: sina_totals(x[3], today) for k, x in VARIETIES.items() if x[2] == "sina"}
                val = sina[c].get(d["dates"][i])
                if val:
                    d["series"][c][i] = val
                    added += 1
                    print("backfilled", c, d["dates"][i], val)
    if added:
        d["updated"] = datetime.datetime.now(BJ).strftime("%Y-%m-%d %H:%M")
        save(d)
    print(f"done, {added} day(s) added, last = {d['dates'][-1]}")


if __name__ == "__main__":
    sys.exit(main())
