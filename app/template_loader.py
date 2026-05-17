from functools import lru_cache
from string import Template

from app.config import get_settings
from app.presets import RESOLUTION_PRESETS


BASE_TEMPLATE_NAME = "base.html"


@lru_cache(maxsize=None)
def load_string_template(template_name: str) -> Template:
    settings = get_settings()
    template_path = settings.templates_dir / template_name
    if not template_path.is_file():
        raise RuntimeError(f"Template file not found: {template_path}")
    return Template(template_path.read_text(encoding="utf-8"))


def validate_required_templates() -> None:
    required_template_names = {
        BASE_TEMPLATE_NAME,
        *(preset.css_template_name for preset in RESOLUTION_PRESETS.values()),
    }
    for template_name in required_template_names:
        load_string_template(template_name)
