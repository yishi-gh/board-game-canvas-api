from dataclasses import dataclass

from app.schemas import PlayerSummary


@dataclass(frozen=True)
class ParsedReport:
    main_markdown: str
    main_html: str
    player: PlayerSummary


@dataclass(frozen=True)
class ResolutionPreset:
    width: int
    height: int
    system_prompt: str
    css_template_name: str


@dataclass(frozen=True)
class RenderedImage:
    image_url: str
    image_base64: str
    mime_type: str
