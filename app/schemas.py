from enum import Enum

from pydantic import AliasChoices, AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator

from app.image_utils import normalize_image_source


class Resolution(str, Enum):
    vertical = "vertical"
    horizontal = "horizontal"
    square = "square"


class GenerateReportRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        protected_namespaces=(),
    )

    model_api_url: AnyHttpUrl = Field(
        ...,
        validation_alias=AliasChoices("model_api_url", "model_url"),
    )
    hcti_api_url: AnyHttpUrl
    resolution: Resolution
    report_md: str = Field(..., min_length=1)
    board_image: str = Field(..., min_length=1)
    rules_md: str = Field(..., min_length=1)
    custom_prompt: str | None = None

    @field_validator("report_md", "rules_md", "board_image")
    @classmethod
    def ensure_not_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Field must not be blank.")
        return value.strip()

    @field_validator("custom_prompt")
    @classmethod
    def normalize_custom_prompt(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("board_image")
    @classmethod
    def validate_board_image(cls, value: str) -> str:
        normalize_image_source(value)
        return value


class PlayerSummary(BaseModel):
    player_id: str
    score: str
    quote: str


class GenerateReportResponse(BaseModel):
    resolution: Resolution
    width: int
    height: int
    background_image: str
    output_image_url: str
    output_image_base64: str
    output_image_mime_type: str
    player: PlayerSummary
