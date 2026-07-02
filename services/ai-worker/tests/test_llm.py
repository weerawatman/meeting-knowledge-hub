from llm.generator import generate_summary, generate_summary_prompted


def test_generate_summary_returns_meeting_summary() -> None:
    """generate_summary should return a MeetingSummary with matching meeting_id.
    Ollama may not be running in CI — the fallback returns a transcript excerpt as summary."""
    summary = generate_summary("Hello meeting transcript", meeting_id="meeting-abc")
    assert summary.meeting_id == "meeting-abc"
    assert isinstance(summary.summary, str)
    assert len(summary.summary) > 0
    assert isinstance(summary.decisions, list)
    assert isinstance(summary.action_items, list)


def test_generate_summary_prompted_content() -> None:
    prompt = generate_summary_prompted("Sample transcript text")
    assert "Sample transcript text" in prompt
    assert "Summarize the transcript in Thai" in prompt
