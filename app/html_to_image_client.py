import requests

from app.config import get_settings
from app.domain import RenderedImage, ResolutionPreset
from app.image_utils import resolve_image_payload
from app.upstream import extract_image_reference, parse_response_payload


def render_png_from_html(
    html_document: str,
    preset: ResolutionPreset,
    hcti_api_url: str | None = None,
) -> RenderedImage:
    settings = get_settings()
    provider = settings.html_to_image_provider

    if provider == "hcti":
        return render_with_hcti(
            html_document=html_document,
            preset=preset,
            hcti_api_url=hcti_api_url,
        )

    if provider == "htmlcsstoimage":
        return render_with_htmlcsstoimage(html_document=html_document, preset=preset)

    raise RuntimeError("Unsupported HTML_TO_IMAGE_PROVIDER. Use 'hcti' or 'htmlcsstoimage'.")


def render_with_hcti(
    html_document: str,
    preset: ResolutionPreset,
    hcti_api_url: str | None = None,
) -> RenderedImage:
    settings = get_settings()
    if not settings.hcti_user_id or not settings.hcti_api_key:
        raise RuntimeError(
            "Missing credentials for HCTI. Set HCTI_USER_ID and HCTI_API_KEY."
        )

    response = requests.post(
        hcti_api_url or settings.hcti_api_url,
        data={
            "html": html_document,
            "viewport_width": preset.width,
            "viewport_height": preset.height,
            "device_scale": 1,
        },
        auth=(settings.hcti_user_id, settings.hcti_api_key),
        timeout=settings.request_timeout_seconds,
    )
    response.raise_for_status()

    payload = parse_response_payload(response)
    image_url = extract_image_reference(payload)
    if not image_url:
        raise RuntimeError("The HCTI response did not contain an output image URL.")

    mime_type, image_base64 = resolve_image_payload(
        image_reference=image_url,
        timeout_seconds=settings.request_timeout_seconds,
    )
    return RenderedImage(
        image_url=image_url,
        image_base64=image_base64,
        mime_type=mime_type,
    )


def render_with_htmlcsstoimage(html_document: str, preset: ResolutionPreset) -> RenderedImage:
    settings = get_settings()
    if not settings.htmlcsstoimage_api_key:
        raise RuntimeError(
            "Missing credentials for HTML/CSS to Image. Set HTMLCSSTOIMAGE_API_KEY."
        )

    response = requests.post(
        settings.htmlcsstoimage_api_url,
        headers={"CLIENT-API-KEY": settings.htmlcsstoimage_api_key},
        json={
            "html_content": html_document,
            "viewPortWidth": preset.width,
            "viewPortHeight": preset.height,
            "generate_img_url": True,
        },
        timeout=settings.request_timeout_seconds,
    )
    response.raise_for_status()

    payload = parse_response_payload(response)
    image_url = extract_image_reference(payload)
    if not image_url:
        raise RuntimeError("The HTML/CSS to Image response did not contain an output image URL.")

    mime_type, image_base64 = resolve_image_payload(
        image_reference=image_url,
        timeout_seconds=settings.request_timeout_seconds,
    )
    return RenderedImage(
        image_url=image_url,
        image_base64=image_base64,
        mime_type=mime_type,
    )
