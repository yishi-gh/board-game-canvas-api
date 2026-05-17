import html

from app.domain import ResolutionPreset
from app.schemas import PlayerSummary
from app.template_loader import BASE_TEMPLATE_NAME, load_string_template


def build_html_document(
    preset: ResolutionPreset,
    background_image: str,
    report_html: str,
    player: PlayerSummary,
) -> str:
    css = load_string_template(preset.css_template_name).substitute(
        width=preset.width,
        height=preset.height,
        background_image=escape_css_url(background_image),
    )
    return load_string_template(BASE_TEMPLATE_NAME).substitute(
        css=css,
        report_html=report_html,
        player_name=html.escape(player.player_id),
        player_score=html.escape(player.score),
        player_quote=html.escape(player.quote),
    )


def escape_css_url(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")
