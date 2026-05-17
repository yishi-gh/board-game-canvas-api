# board-game-canvas-api

基于 FastAPI + Mangum 的服务端图片生成 API，用于接收桌游战报参数、调用上游生图模型、拼装 HTML/CSS 模板，并输出最终战报图片。

项目不依赖仓库内 `.env` 文件。运行时配置统一从系统环境变量或 Vercel 环境变量读取。

相关补充：

- [Codex规划文档](D:/mine/board-game-canvas-api/Codex规划文档.md)

## 概览

- 核心接口：`POST /api/v1/generate_report`
- 健康检查：`GET /`、`GET /healthz`
- 模板资源：`templates/base.html` + `templates/*.css`
- 运行模式：服务端读取模板，内联 CSS，交给转图服务渲染

## 部署

### 本地启动

```powershell
cd D:\mine\board-game-canvas-api
uv sync
```

设置环境变量。使用 `hcti` 示例：

```powershell
$env:HTML_TO_IMAGE_PROVIDER="hcti"
$env:HCTI_USER_ID="your_user_id"
$env:HCTI_API_KEY="your_api_key"
```

如果使用 `htmlcsstoimage`：

```powershell
$env:HTML_TO_IMAGE_PROVIDER="htmlcsstoimage"
$env:HTMLCSSTOIMAGE_API_KEY="your_api_key"
```

如果上游 `model_url` 需要统一鉴权：

```powershell
$env:MODEL_API_KEY="your_model_api_key"
$env:MODEL_API_HEADER="Authorization"
$env:MODEL_API_AUTH_SCHEME="Bearer"
```

启动服务：

```powershell
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

本地地址：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/healthz`
- `http://127.0.0.1:8000/api/v1/generate_report`

### Vercel 部署

1. 将代码推送到 GitHub
2. 在 Vercel 导入仓库
3. 配置环境变量
4. 执行部署

环境变量：

- 使用 `hcti`
  - `HTML_TO_IMAGE_PROVIDER=hcti`
  - `HCTI_USER_ID`
  - `HCTI_API_KEY`
- 使用 `htmlcsstoimage`
  - `HTML_TO_IMAGE_PROVIDER=htmlcsstoimage`
  - `HTMLCSSTOIMAGE_API_KEY`
- 如果上游模型统一需要鉴权
  - `MODEL_API_KEY`
  - `MODEL_API_HEADER`
  - `MODEL_API_AUTH_SCHEME`

## API 使用

### 接口

- `POST /api/v1/generate_report`

### 请求参数

- `model_url`：上游生图模型接口地址
- `resolution`：`vertical`、`horizontal`、`square`
- `report_md`：战报 Markdown
- `board_image`：版图图片，支持 URL、Data URI、纯 Base64
- `rules_md`：规则解析 Markdown
- `custom_prompt`：可选补充提示词

请求示例：

```json
{
  "model_url": "https://your-model-api.example.com/generate",
  "resolution": "vertical",
  "report_md": "# 战报标题\n这里是战报正文\n\n- ID: 玩家甲\n- Score: 120\n- Quote: 控场完美。",
  "board_image": "https://example.com/board.png",
  "rules_md": "# 规则解析\n这里是规则说明",
  "custom_prompt": "epic strategy battle report background"
}
```

`curl` 示例：

```bash
curl -X POST "https://your-domain.vercel.app/api/v1/generate_report" \
  -H "Content-Type: application/json" \
  -d '{
    "model_url": "https://your-model-api.example.com/generate",
    "resolution": "vertical",
    "report_md": "# 标题\n正文...\n\n- ID: 玩家甲\n- Score: 120\n- Quote: 控场完美。",
    "board_image": "https://example.com/board.png",
    "rules_md": "# 规则\n这里是规则解析",
    "custom_prompt": "epic strategy battle report background"
  }'
```

### 返回字段

- `background_image`
- `output_image_url`
- `output_image_base64`
- `output_image_mime_type`
- `player`

返回示例：

```json
{
  "resolution": "vertical",
  "width": 1080,
  "height": 1920,
  "background_image": "https://example.com/background.png",
  "output_image_url": "https://example.com/final-report.png",
  "output_image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "output_image_mime_type": "image/png",
  "player": {
    "player_id": "玩家甲",
    "score": "120",
    "quote": "控场完美。"
  }
}
```

## 手动测试

仓库内提供交互式测试脚本：

```powershell
uv run python scripts/manual_generate_report.py
```

脚本会要求输入：

- API Base URL
- `model_url`
- `resolution`
- `board_image`
- `report_md`
- `rules_md`
- `custom_prompt`

成功后会把返回图片保存到 `outputs/` 目录。

## 项目结构

```text
board-game-canvas-api/
├── api/
│   └── main.py
├── app/
│   ├── api.py
│   ├── config.py
│   ├── domain.py
│   ├── html_to_image_client.py
│   ├── image_utils.py
│   ├── markdown_parser.py
│   ├── model_client.py
│   ├── presets.py
│   ├── rendering.py
│   ├── report_service.py
│   ├── schemas.py
│   ├── template_loader.py
│   └── upstream.py
├── scripts/
│   └── manual_generate_report.py
├── templates/
├── .python-version
├── pyproject.toml
├── vercel.json
└── Codex规划文档.md
```

## 说明

- 模板文件存在 `templates/` 中，但最终会在服务端运行时注入为内联 HTML/CSS
- 当前项目是小型单接口 API，复杂度主要来自外部服务编排
- 当前更适合单租户或受控场景，因为 `MODEL_API_KEY` 是服务端全局配置
