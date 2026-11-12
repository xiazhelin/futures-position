"""品种配置与读写工具。新增品种只需在 VARIETIES 里加一行。"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "positions.json")

# code: (中文名, 交易所, 数据源, 源内代码, 板块)
VARIETIES = {
    "RU": ("天然橡胶", "SHFE", "shfe", "ru_f", "橡胶"),
    "NR": ("20号胶", "INE", "shfe", "nr_f", "橡胶"),
    "BR": ("丁二烯橡胶", "SHFE", "shfe", "br_f", "橡胶"),
    "RB": ("螺纹钢", "SHFE", "shfe", "rb_f", "黑色"),
    "HC": ("热轧卷板", "SHFE", "shfe", "hc_f", "黑色"),
    "JM": ("焦煤", "DCE", "sina", "JM", "黑色"),
    "J": ("焦炭", "DCE", "sina", "J", "黑色"),
    "I": ("铁矿石", "DCE", "sina", "I", "黑色"),
}


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def save(d):
    d["varieties"] = [
        {"code": c, "name": v[0], "exchange": v[1], "group": v[4],
         "source": "上期所日行情" if v[2] == "shfe" else "新浪财经(分合约加总)"}
        for c, v in VARIETIES.items()
    ]
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, separators=(",", ":"))
