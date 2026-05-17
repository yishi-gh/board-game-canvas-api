import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Callable

import requests


ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"
SUPPORTED_IMAGE_EXTENSIONS = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def prompt(message: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    raw_value = input(f"{message}{suffix}: ").strip()
    if raw_value:
        return raw_value
    if default is not None:
        return default
    return ""


def prompt_required(message: str, default: str | None = None) -> str:
    while True:
        value = prompt(message, default=default)
        if value:
            return value
        print("该字段不能为空，请重新输入。")


def prompt_multiline(message: str) -> str:
    print(f"{message}，输入完成后单独输入 END 并回车：")
    lines: list[str] = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    content = "\n".join(lines).strip()
    if not content:
        raise ValueError(f"{message}不能为空。")
    return content


def prompt_optional_multiline(message: str) -> str | None:
    print(f"{message}，可留空。若要输入，多行结束后单独输入 END 并回车；直接回车则跳过：")
    first_line = input()
    if not first_line.strip():
        return None

    lines = [first_line]
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    content = "\n".join(lines).strip()
    return content or None


def prompt_choice(message: str, allowed_values: set[str], default: str) -> str:
    allowed_display = "/".join(sorted(allowed_values))
    while True:
        value = prompt(f"{message} ({allowed_display})", default=default).lower()
        if value in allowed_values:
            return value
        print(f"无效选项，请输入以下值之一：{allowed_display}")


def prompt_board_image() -> str:
    source_type = prompt_choice(
        "版图图片输入方式",
        allowed_values={"url", "file", "base64"},
        default="file",
    )
    if source_type == "url":
        return prompt_required("请输入版图图片 URL")
    if source_type == "base64":
        return prompt_required("请输入版图图片 Base64 或 Data URI")
    return load_local_image_as_data_uri(prompt_required("请输入本地图片路径"))


def load_local_image_as_data_uri(raw_path: str) -> str:
    image_path = Path(raw_path).expanduser()
    if not image_path.is_absolute():
        image_path = (Path.cwd() / image_path).resolve()

    if not image_path.is_file():
        raise FileNotFoundError(f"未找到图片文件: {image_path}")

    mime_type = SUPPORTED_IMAGE_EXTENSIONS.get(image_path.suffix.lower())
    if not mime_type:
        raise ValueError(
            "不支持的图片扩展名，仅支持: "
            + ", ".join(sorted(SUPPORTED_IMAGE_EXTENSIONS))
        )

    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def build_payload() -> dict[str, str]:
    model_url = prompt_required("请输入 model_url")
    resolution = prompt_choice(
        "请输入分辨率",
        allowed_values={"vertical", "horizontal", "square"},
        default="vertical",
    )
    board_image = prompt_board_image()
    report_md = prompt_multiline("请输入战报 Markdown")
    rules_md = prompt_multiline("请输入规则解析 Markdown")
    custom_prompt = prompt_optional_multiline("请输入 custom_prompt")

    payload: dict[str, str] = {
        "model_url": model_url,
        "resolution": resolution,
        "report_md": report_md,
        "board_image": board_image,
        "rules_md": rules_md,
    }
    if custom_prompt:
        payload["custom_prompt"] = custom_prompt
    return payload


def post_generate_report(api_base_url: str, payload: dict[str, str]) -> dict:
    endpoint = f"{api_base_url.rstrip('/')}/api/v1/generate_report"
    response = requests.post(
        endpoint,
        json=payload,
        timeout=300,
    )

    if not response.ok:
        raise RuntimeError(
            "API 调用失败:\n"
            f"status={response.status_code}\n"
            f"body={response.text}"
        )
    return response.json()


def save_output_image(response_payload: dict, output_path: Path | None = None) -> Path:
    output_base64 = response_payload.get("output_image_base64")
    if not output_base64:
        raise RuntimeError("响应中缺少 output_image_base64，无法落盘图片。")

    if output_path is None:
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = OUTPUTS_DIR / f"battle-report-{timestamp}.png"
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    output_bytes = base64.b64decode(output_base64)
    output_path.write_bytes(output_bytes)
    return output_path


def print_response_summary(response_payload: dict, image_path: Path) -> None:
    player = response_payload.get("player", {})
    print()
    print("生成成功。")
    print(f"图片已保存: {image_path}")
    print(f"背景图: {response_payload.get('background_image', '')}")
    print(f"输出图 URL: {response_payload.get('output_image_url', '')}")
    print(f"分辨率: {response_payload.get('width')}x{response_payload.get('height')}")
    print(
        "玩家摘要: "
        f"{player.get('player_id', '')} / "
        f"{player.get('score', '')} / "
        f"{player.get('quote', '')}"
    )


def maybe_save_request_payload(payload: dict) -> None:
    answer = prompt_choice(
        "是否把本次请求参数保存为 JSON 文件",
        allowed_values={"y", "n"},
        default="n",
    )
    if answer != "y":
        return

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target_path = OUTPUTS_DIR / f"battle-report-request-{timestamp}.json"
    target_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"请求参数已保存: {target_path}")


def main() -> None:
    print("board-game-canvas-api 手动测试客户端")
    api_base_url = prompt_required("请输入 API Base URL", default=DEFAULT_API_BASE_URL)
    payload = build_payload()
    maybe_save_request_payload(payload)
    response_payload = post_generate_report(api_base_url=api_base_url, payload=payload)
    image_path = save_output_image(response_payload)
    print_response_summary(response_payload, image_path)


if __name__ == "__main__":
    main()
