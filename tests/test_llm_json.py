from profile_summary.llm_json import parse_summary_object


def test_parses_fenced_json_and_flattens_whitespace() -> None:
    result = parse_summary_object(
        '```json\n{"Profile": "The client is active.\\nMorning visits preferred."}\n```'
    )

    assert result == {
        "Profile": "The client is active. Morning visits preferred."
    }


def test_markdown_fallback_returns_flat_json_values() -> None:
    result = parse_summary_object(
        "## Profile\nThe client is active.\nMorning visits preferred."
    )

    assert result == {
        "Profile": "The client is active. Morning visits preferred."
    }
