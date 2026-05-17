from app.domain import ResolutionPreset
from app.schemas import Resolution


RESOLUTION_PRESETS: dict[Resolution, ResolutionPreset] = {
    Resolution.vertical: ResolutionPreset(
        width=1080,
        height=1920,
        system_prompt=(
            "A vertical 9:16 thematic background. The top 70% is empty with dark "
            "semi-transparent texture for overlaying long text. Visual elements are "
            "clustered in the middle. The bottom-right corner has an explicit empty "
            "glowing neon/stone decorative frame border for stats. ABSOLUTELY NO "
            "GENERATED TEXT SEED."
        ),
        css_template_name="vertical.css",
    ),
    Resolution.horizontal: ResolutionPreset(
        width=1920,
        height=1080,
        system_prompt=(
            "A horizontal 16:9 landscape layout. The left 60% area is dimmed and "
            "clear for text overlay. The right-bottom area has a distinct empty box "
            "for score presentation."
        ),
        css_template_name="horizontal.css",
    ),
    Resolution.square: ResolutionPreset(
        width=1200,
        height=1200,
        system_prompt=(
            "A 1:1 square canvas. Centered artwork with a translucent dark card "
            "overlay in the middle for text, and a designated empty label slot at "
            "the bottom-right for summary data."
        ),
        css_template_name="square.css",
    ),
}
