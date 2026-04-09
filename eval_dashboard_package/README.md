# 评估看板 Dashboard

## 目录结构

```
output/                    # 最终产物
  viz_final_v10_full.html  # 完整自包含看板（可直接部署）

scripts/                   # 所有构建与修复脚本
  build_v10*.py            # v10 主构建脚本
  auto_build.py            # 自动构建流水线
  add_tab3.py              # Tab3 历次评估趋势
  fix[2-11]*.py            # 增量修复脚本（按序执行）
  fix_*.py                 # 其他修复脚本
  build_*.py               # 早期版本构建脚本

data/                      # 数据文件
  score_notes.json         # 打分备注数据（来自飞书）
  prompt_ids.json          # Prompt ID 映射
  cases_data*.json         # 案例数据（各版本）
  llm_data*.json           # LLM评估数据
```

## 部署方式

最终产物 `output/viz_final_v10_full.html` 为完全自包含的单文件，
内联了 Chart.js 4.4.1、chartjs-plugin-datalabels 2.2.0、SheetJS。

直接放到任意静态服务器（Nginx / S3 / Vercel / GitHub Pages 等）即可访问。

## 三个 Tab

| Tab | 说明 |
|-----|------|
| 3月流式竞对 | 豆包 vs Qwen3.5，含数据看板 + 案例探查 |
| LLM竞品评估 | 豆包 vs 千问3/Gemini 3 Pro/GPT 5.2，含 p-value 显著性着色 + 打分备注 |
| 历次评估趋势 | 跨期指标汇总表 + 趋势折线图 |

## 增量修复脚本说明

| 脚本 | 功能 |
|------|------|
| fix2.py | 初始样式修复 |
| fix3.py / fix3_v2.py | 图表与布局修复 |
| fix4.py | 案例探查一页一题、Tab 重命名 |
| fix5.py | 注入打分备注数据 |
| fix5b.py | CSS 选择器修复 + 备注渲染 |
| fix6.py | Tab2 拆分为 数据看板/案例探查 子Tab |
| fix7.py | 子Tab导航位置调整 |
| fix8.py | 子Tab内容区宽度对齐 |
| fix9.py | Tab2 GSB 改为"豆包 vs X"格式 |
| fix10.py | Tab3 GSB 改为"豆包 vs X"格式 |
| fix11.py | p-value 显著性说明 + 着色（指标卡片）|
| fix11b.py | p-value 图表着色同步更新 |
