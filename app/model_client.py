import requests

from app.config import get_settings
from app.domain import ResolutionPreset
from app.schemas import Resolution
from app.upstream import extract_image_reference, parse_response_payload


def generate_background_image(
    model_url: str,
    resolution: Resolution,
    preset: ResolutionPreset,
    report_main_markdown: str,
    rules_markdown: str,
    board_image_source: str,
    custom_prompt: str | None,
) -> str:
    settings = get_settings()
    prompt_parts = [
        preset.system_prompt,
        "Use the supplied board image as the primary spatial reference.",
        f"Rule summary:\n{rules_markdown.strip()}",
        f"Battle report excerpt:\n{build_excerpt(report_main_markdown)}",
    ]
    if custom_prompt:
        prompt_parts.append(f"User refinement:\n{custom_prompt}")

    payload = {
        "prompt": "\n\n".join(prompt_parts),
        "resolution": {
            "name": resolution.value,
            "width": preset.width,
            "height": preset.height,
        },
        "board_image": board_image_source,
        "response_format": "url",
        "metadata": {
            "service": "board-game-canvas-api",
            "target": "background-only",
        },
    }
    response = requests.post(
        model_url,
        json=payload,
        headers=build_model_headers(),
        timeout=settings.request_timeout_seconds,
    )
    response.raise_for_status()

    image_reference = extract_image_reference(parse_response_payload(response))
    if not image_reference:
        raise RuntimeError("The model service response did not contain a usable image reference.")
    return image_reference


def build_model_headers() -> dict[str, str]:
    settings = get_settings()
    headers = {"Content-Type": "application/json"}
    if not settings.model_api_key:
        return headers

    if (
        settings.model_api_header.lower() == "authorization"
        and not settings.model_api_key.lower().startswith(("bearer ", "basic "))
    ):
        headers[settings.model_api_header] = (
            f"{settings.model_api_auth_scheme} {settings.model_api_key}"
        )
    else:
        headers[settings.model_api_header] = settings.model_api_key
    return headers


def build_excerpt(text: str, limit: int = 1200) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[:limit].rstrip()}..."
