from typing import Any

import requests

from app.image_utils import normalize_external_image_reference


def parse_response_payload(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        text = response.text.strip()
        if not text:
            return {}
        return text


def extract_image_reference(payload: Any) -> str | None:
    if isinstance(payload, str):
        return normalize_external_image_reference(payload)

    if isinstance(payload, list):
        for item in payload:
            image_reference = extract_image_reference(item)
            if image_reference:
                return image_reference
        return None

    if isinstance(payload, dict):
        for key in (
            "image_url",
            "url",
            "image",
            "src",
            "background_image",
            "output",
            "result",
            "render_url",
            "screenshot_url",
        ):
            if key in payload:
                image_reference = extract_image_reference(payload[key])
                if image_reference:
                    return image_reference

        for key in ("data", "images", "result", "output", "artifacts"):
            if key in payload:
                image_reference = extract_image_reference(payload[key])
                if image_reference:
                    return image_reference

    return None
