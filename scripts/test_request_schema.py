from app.schemas import GenerateReportRequest


BASE_PAYLOAD = {
    "resolution": "vertical",
    "report_md": "# 标题\n正文\n\n- ID: 玩家甲\n- Score: 120\n- Quote: 控场完美。",
    "board_image": "https://example.com/board.png",
    "rules_md": "# 规则\n说明",
}


def test_accepts_model_api_url() -> None:
    payload = {
        **BASE_PAYLOAD,
        "model_api_url": "https://model.example.com/generate",
        "hcti_api_url": "https://hcti.io/v1/image",
    }
    request = GenerateReportRequest.model_validate(payload)
    assert str(request.model_api_url) == "https://model.example.com/generate"
    assert str(request.hcti_api_url) == "https://hcti.io/v1/image"


def test_accepts_legacy_model_url_alias() -> None:
    payload = {
        **BASE_PAYLOAD,
        "model_url": "https://model.example.com/generate",
        "hcti_api_url": "https://hcti.io/v1/image",
    }
    request = GenerateReportRequest.model_validate(payload)
    assert str(request.model_api_url) == "https://model.example.com/generate"


def test_requires_hcti_api_url() -> None:
    payload = {
        **BASE_PAYLOAD,
        "model_api_url": "https://model.example.com/generate",
    }
    try:
        GenerateReportRequest.model_validate(payload)
    except Exception as exc:
        assert "hcti_api_url" in str(exc)
        return
    raise AssertionError("Expected validation error for missing hcti_api_url.")


def main() -> None:
    test_accepts_model_api_url()
    test_accepts_legacy_model_url_alias()
    test_requires_hcti_api_url()
    print("schema tests passed")


if __name__ == "__main__":
    main()
