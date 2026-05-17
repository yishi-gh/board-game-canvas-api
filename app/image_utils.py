import base64
import binascii
import re

import requests


DEFAULT_OUTPUT_MIME_TYPE = "image/png"
URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)
DATA_URI_PATTERN = re.compile(
    r"^data:(?P<mime>image/[a-zA-Z0-9.+-]+);base64,(?P<data>.+)$",
    re.IGNORECASE | re.DOTALL,
)


def normalize_image_source(value: str) -> str:
    candidate = value.strip()
    if URL_PATTERN.match(candidate):
        return candidate

    data_uri_match = DATA_URI_PATTERN.match(candidate)
    if data_uri_match:
        compact = re.sub(r"\s+", "", data_uri_match.group("data"))
        validate_base64_payload(compact)
        return f"data:{data_uri_match.group('mime')};base64,{compact}"

    compact = re.sub(r"\s+", "", candidate)
    validate_base64_payload(compact)
    return f"data:{DEFAULT_OUTPUT_MIME_TYPE};base64,{compact}"


def validate_base64_payload(value: str) -> None:
    try:
        base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("board_image must be a valid image URL or Base64 string.") from exc


def normalize_external_image_reference(value: str) -> str | None:
    candidate = value.strip()
    if not candidate:
        return None
    if URL_PATTERN.match(candidate):
        return candidate

    data_uri_match = DATA_URI_PATTERN.match(candidate)
    if data_uri_match:
        compact = re.sub(r"\s+", "", data_uri_match.group("data"))
        validate_base64_payload(compact)
        return f"data:{data_uri_match.group('mime')};base64,{compact}"

    compact = re.sub(r"\s+", "", candidate)
    if len(compact) < 64:
        return None

    try:
        validate_base64_payload(compact)
    except ValueError:
        return None
    return f"data:{DEFAULT_OUTPUT_MIME_TYPE};base64,{compact}"


def resolve_image_payload(image_reference: str, timeout_seconds: int) -> tuple[str, str]:
    data_uri_match = DATA_URI_PATTERN.match(image_reference)
    if data_uri_match:
        return data_uri_match.group("mime"), re.sub(r"\s+", "", data_uri_match.group("data"))

    response = requests.get(image_reference, timeout=timeout_seconds)
    response.raise_for_status()
    mime_type = response.headers.get("Content-Type", DEFAULT_OUTPUT_MIME_TYPE).split(";")[0].strip()
    image_base64 = base64.b64encode(response.content).decode("ascii")
    return mime_type or DEFAULT_OUTPUT_MIME_TYPE, image_base64
