from app.html_to_image_client import render_png_from_html
from app.image_utils import normalize_image_source
from app.markdown_parser import parse_report_markdown
from app.model_client import generate_background_image
from app.presets import RESOLUTION_PRESETS
from app.rendering import build_html_document
from app.schemas import GenerateReportRequest, GenerateReportResponse


def generate_report(payload: GenerateReportRequest) -> GenerateReportResponse:
    preset = RESOLUTION_PRESETS[payload.resolution]
    parsed_report = parse_report_markdown(payload.report_md)
    board_image_source = normalize_image_source(payload.board_image)

    background_image = generate_background_image(
        model_url=str(payload.model_url),
        resolution=payload.resolution,
        preset=preset,
        report_main_markdown=parsed_report.main_markdown,
        rules_markdown=payload.rules_md,
        board_image_source=board_image_source,
        custom_prompt=payload.custom_prompt,
    )
    html_document = build_html_document(
        preset=preset,
        background_image=background_image,
        report_html=parsed_report.main_html,
        player=parsed_report.player,
    )
    rendered_image = render_png_from_html(
        html_document=html_document,
        preset=preset,
    )
    return GenerateReportResponse(
        resolution=payload.resolution,
        width=preset.width,
        height=preset.height,
        background_image=background_image,
        output_image_url=rendered_image.image_url,
        output_image_base64=rendered_image.image_base64,
        output_image_mime_type=rendered_image.mime_type,
        player=parsed_report.player,
    )
