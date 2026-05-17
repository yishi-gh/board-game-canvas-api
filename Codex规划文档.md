# Codex 规划文档

## 1. 目标

将项目实现为一个可部署的服务端 API，并整理成便于后续维护的代码结构与文档结构。

最终项目名统一为 `board-game-canvas-api`。

## 2. 设计决策

### 2.1 项目定位

- 项目是服务端 API，不是前端页面项目。
- 调用方传业务参数。
- 第三方服务凭证由服务端环境变量管理。

### 2.2 模板策略

- 模板作为项目资源放在 `templates/` 目录。
- API 运行时读取模板文件。
- 最终将 CSS 内联注入 HTML，再交给转图服务渲染。

这样做的原因：

- 符合 Serverless 场景
- 不依赖额外静态资源地址
- 方便第三方 HTML-to-Image 服务直接消费

### 2.3 模块拆分

将原本过长的 `api/main.py` 拆成：

- `app/api.py`：FastAPI 应用与路由
- `app/config.py`：运行时配置
- `app/schemas.py`：请求/响应模型
- `app/report_service.py`：主流程编排
- `app/model_client.py`：模型服务调用
- `app/html_to_image_client.py`：转图服务调用
- `app/markdown_parser.py`：Markdown 切片
- `app/rendering.py`：HTML/CSS 注入
- `app/template_loader.py`：模板读取与校验
- `app/image_utils.py`：图片与 Base64 工具
- `app/upstream.py`：上游响应解析
- `app/presets.py`：分辨率预设
- `app/domain.py`：内部数据结构

`api/main.py` 保持为轻量入口，仅负责暴露 `app` 和 `handler`。

### 2.4 环境变量策略

- 不依赖仓库内 `.env`
- 统一读取操作系统环境变量或 Vercel 环境变量
- 避免把服务端配置伪装成 API 调用参数

### 2.5 依赖管理

- 使用 `uv`
- 使用 `pyproject.toml`
- 移除 `requirements.txt`

### 2.6 手动测试策略

- 提供交互式脚本 `scripts/manual_generate_report.py`
- 允许手动输入接口地址、模型地址、Markdown、图片等内容
- 自动将 API 返回的 Base64 图片写入 `outputs/`

## 3. 已完成工作

- 完成项目主接口 `POST /api/v1/generate_report`
- 完成请求参数校验
- 完成 Markdown 玩家信息切片
- 完成三套模板与分辨率预设
- 完成上游模型调用逻辑
- 完成 HTML-to-Image 调用逻辑
- 完成 Vercel 入口与模板资源打包配置
- 完成模块化重构
- 完成手动测试脚本
- 完成文档收敛与命名统一

## 4. 当前边界

- 当前项目是小型单接口 API
- 没有数据库
- 没有用户鉴权
- 没有任务队列
- 没有缓存层
- 没有后台管理

它的复杂度主要来自外部服务编排，不来自系统规模。

## 5. 后续可扩展方向

- 增加自动化测试
- 增加接口示例集合
- 增加部署检查清单
- 增加多租户模型配置能力
- 增加失败重试、日志和监控
