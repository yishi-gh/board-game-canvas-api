import re

import mistune

from app.domain import ParsedReport
from app.schemas import PlayerSummary


PLAYER_SECTION_PATTERN = re.compile(
    r"""
    (?P<body>.*?)
    (?:\r?\n){1,3}
    [ \t]*[-*]\s*ID\s*:\s*(?P<player_id>[^\r\n]+?)\s*\r?\n
    [ \t]*[-*]\s*Score\s*:\s*(?P<score>[^\r\n]+?)\s*\r?\n
    [ \t]*[-*]\s*Quote\s*:\s*(?P<quote>[^\r\n]+?)\s*
    \Z
    """,
    re.IGNORECASE | re.DOTALL | re.VERBOSE,
)

markdown_renderer = mistune.create_markdown(escape=True)


def parse_report_markdown(report_markdown: str) -> ParsedReport:
    match = PLAYER_SECTION_PATTERN.search(report_markdown.strip())
    if not match:
        raise ValueError(
            "report_md must end with player metadata lines in the format "
            "'- ID: ...', '- Score: ...', '- Quote: ...'."
        )

    main_markdown = match.group("body").strip()
    if not main_markdown:
        raise ValueError("report_md main content cannot be empty after removing player metadata.")

    player = PlayerSummary(
        player_id=match.group("player_id").strip(),
        score=match.group("score").strip(),
        quote=match.group("quote").strip(),
    )
    main_html = markdown_renderer(main_markdown)
    return ParsedReport(main_markdown=main_markdown, main_html=main_html, player=player)
