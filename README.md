# Genshin Radar

每天由 GitHub Actions 自动运行 [OpenCode](https://opencode.ai)，联网检索《原神》的版本更新、卡池、活动与公告，更新 `site/data.json`，并部署到 GitHub Pages。

## 工作流程

1. `.github/workflows/daily-update.yml` 每天北京时间 08:17 运行（也可在 Actions 页面手动触发）。
2. OpenCode 按照 `.github/prompts/daily-update.md` 的指令，用 `websearch` / `webfetch` 检索信息并改写 `site/data.json`。
3. 工作流丢弃 `site/data.json` 以外的所有改动，用 `scripts/validate_data.py` 校验结构；不合格则任务失败，不会提交。
4. 有变化时自动提交，然后调用 `.github/workflows/pages.yml` 把 `site/` 部署到 GitHub Pages。

`site/index.html` 是静态页面，只负责读取并展示 `data.json`，AI 不会修改它。

## 配置

1. **Settings → Pages → Source** 选择 **GitHub Actions**。
2. **Settings → Secrets and variables → Actions**：
   - Secret `ANTHROPIC_API_KEY`（默认模型所需）。
   - 可选：变量 `OPENCODE_MODEL` 换用其他模型，格式为 `provider/model`，例如 `openai/gpt-5`、`deepseek/deepseek-chat`，并添加对应的 `OPENAI_API_KEY` / `DEEPSEEK_API_KEY` / `OPENROUTER_API_KEY` secret。
3. 在 Actions 页面手动运行一次 **Daily update** 以生成首批数据。

## 本地运行

```bash
npm install -g opencode-ai
OPENCODE_ENABLE_EXA=1 opencode run "$(cat .github/prompts/daily-update.md)"
python3 scripts/validate_data.py
python3 -m http.server -d site 8000
```
