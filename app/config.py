import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


def _read_optional_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _read_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        return default

    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be an integer.") from exc


@dataclass(frozen=True)
class Settings:
    root_dir: Path
    templates_dir: Path
    request_timeout_seconds: int
    html_to_image_provider: str
    hcti_api_url: str
    hcti_user_id: str | None
    hcti_api_key: str | None
    htmlcsstoimage_api_url: str
    htmlcsstoimage_api_key: str | None
    model_api_key: str | None
    model_api_header: str
    model_api_auth_scheme: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        root_dir=ROOT_DIR,
        templates_dir=ROOT_DIR / "templates",
        request_timeout_seconds=_read_int_env("REQUEST_TIMEOUT_SECONDS", 60),
        html_to_image_provider=os.getenv("HTML_TO_IMAGE_PROVIDER", "hcti").strip().lower(),
        hcti_api_url=os.getenv("HCTI_API_URL", "https://hcti.io/v1/image").strip(),
        hcti_user_id=_read_optional_env("HCTI_USER_ID"),
        hcti_api_key=_read_optional_env("HCTI_API_KEY"),
        htmlcsstoimage_api_url=os.getenv(
            "HTMLCSSTOIMAGE_API_URL",
            "https://api.htmlcsstoimg.com/api/v1/generateImage",
        ).strip(),
        htmlcsstoimage_api_key=_read_optional_env("HTMLCSSTOIMAGE_API_KEY"),
        model_api_key=_read_optional_env("MODEL_API_KEY"),
        model_api_header=os.getenv("MODEL_API_HEADER", "Authorization").strip(),
        model_api_auth_scheme=os.getenv("MODEL_API_AUTH_SCHEME", "Bearer").strip(),
    )
