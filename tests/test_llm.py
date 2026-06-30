from llm.generator import generate_summary, generate_summary_prompted


def test_generate_summary_creates_placeholder_summary() -> None:
    summary = generate_summary("Hello meeting transcript", meeting_id="meeting-abc")
    assert summary.meeting_id == "meeting-abc"
    assert summary.summary.startswith("This is a placeholder summary")
    assert len(summary.decisions) >= 1
    assert len(summary.action_items) >= 1


def test_generate_summary_prompted_content() -> None:
    prompt = generate_summary_prompted("Sample transcript text")
    assert "Sample transcript text" in prompt
    assert "Summarize the transcript in Thai" in prompt
