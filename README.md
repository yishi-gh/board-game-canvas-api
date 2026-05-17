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

## 工作原理

请求进入 `POST /api/v1/generate_report` 后，服务端会按固定链路处理每个参数。

### 参数去向

| 参数 | 作用 |
| --- | --- |
| `model_api_url` | 作为上游生图模型地址，由服务端发起请求生成背景图。兼容旧字段 `model_url`，但推荐使用新名字。 |
| `hcti_api_url` | 作为 HCTI 转图接口地址传入请求体，用于生成最终成品图。 |
| `resolution` | 选择画布尺寸、背景图提示词预设，以及最终使用的 CSS 模板。 |
| `report_md` | 拆成“战报正文”和“玩家摘要”两部分；正文转 HTML，摘要用于右下角信息区。 |
| `board_image` | 作为版图参考图传给上游模型，支持 URL、Data URI、纯 Base64。 |
| `rules_md` | 作为规则摘要传给上游模型，帮助生成更贴合战报内容的背景。 |
| `custom_prompt` | 可选补充提示词，追加到上游模型请求中。 |

### 处理流程

1. 服务端先校验请求参数。
   `model_api_url` 和 `hcti_api_url` 都必须是合法 HTTP 地址，`resolution` 只能是 `vertical`、`horizontal`、`square`，`report_md`、`board_image`、`rules_md` 不能为空。

2. `board_image` 会先被标准化。
   如果传入的是 URL，就原样使用；如果传入的是 Data URI 或纯 Base64，服务端会校验后统一整理成可继续传递的图片引用格式。

3. `report_md` 会被拆解。
   它必须以这三行结尾：`- ID: ...`、`- Score: ...`、`- Quote: ...`。这三行会被提取成 `player` 信息，其余正文部分会转成 HTML，作为最终战报主内容。

4. `resolution` 会选中一套预设。
   预设同时决定最终宽高、给上游模型的构图提示词，以及使用哪份 CSS 模板：
   `vertical = 1080 x 1920`，`horizontal = 1920 x 1080`，`square = 1200 x 1200`。

5. 服务端调用 `model_api_url` 生成背景图。
   请求里会带上分辨率信息、规则摘要、战报正文摘录、版图参考图，以及可选的 `custom_prompt`。上游返回的图片地址会作为 `background_image`。

6. 服务端拼装最终 HTML。
   `templates/base.html` 会加载对应分辨率的 CSS 模板，把 `background_image` 注入背景层，把 `report_md` 转出的 HTML 注入正文区域，再把 `ID / Score / Quote` 注入玩家信息区域。

7. 服务端把 HTML 交给转图供应商。
   当前支持 `hcti` 和 `htmlcsstoimage`。当供应商为 `hcti` 时，请求中的 `hcti_api_url` 会作为本次调用的转图接口地址；供应商接收完整 HTML 和视口尺寸，返回最终成品图地址。

8. 服务端组装响应并返回。
   返回值里包含背景图地址 `background_image`、最终图片地址 `output_image_url`、最终图片 Base64 `output_image_base64`、图片类型 `output_image_mime_type`，以及从 `report_md` 中提取出的 `player` 信息。

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

如果上游 `model_api_url` 需要统一鉴权：

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
  - `HCTI_API_URL`
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

- `model_api_url`：上游生图模型接口地址，兼容旧字段 `model_url`
- `hcti_api_url`：HCTI 转图接口地址，例如 `https://hcti.io/v1/image`
- `resolution`：`vertical`、`horizontal`、`square`
- `report_md`：战报 Markdown
- `board_image`：版图图片，支持 URL、Data URI、纯 Base64
- `rules_md`：规则解析 Markdown
- `custom_prompt`：可选补充提示词

请求示例：

```json
{
  "model_api_url": "https://your-model-api.example.com/generate",
  "hcti_api_url": "https://hcti.io/v1/image",
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
    "model_api_url": "https://your-model-api.example.com/generate",
    "hcti_api_url": "https://hcti.io/v1/image",
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
- `model_api_url`
- `hcti_api_url`
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
