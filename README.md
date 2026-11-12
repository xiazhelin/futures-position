# 期货持仓分析

静态网页（GitHub Pages）+ GitHub Actions 每日自动更新持仓数据。

- `index.html`：页面（ECharts），读取 `data/positions.json`
- `scripts/update_positions.py`：增量更新（仅标准库）。上期所/能源中心品种取交易所官方日行情；大商所品种取新浪分合约持仓加总
- `scripts/seed_from_xlsx.py`：用钢联导出的 Excel 初始化历史（需 `pip install openpyxl`）
- `scripts/common.py`：品种配置，新增品种在 `VARIETIES` 里加一行
- `.github/workflows/update.yml`：交易日北京时间 17:30、21:00 自动运行

## 发布
1. 新建 GitHub 仓库，把本目录全部文件推上去
2. Settings → Pages → Source 选 `Deploy from a branch`，分支 `main`、目录 `/ (root)`
3. Settings → Actions → General → Workflow permissions 选 `Read and write permissions`
4. Actions 页面手动 Run 一次 `update-positions` 验证

本地预览：`python -m http.server` 后打开 http://localhost:8000
