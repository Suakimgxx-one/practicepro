import json
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
from analysis_engine.dynamics import DynamicsComparisonResult, DynamicsDeviationPoint
from analysis_engine.feedback import build_analysis_summary, generate_feedback
from analysis_engine.pitch import PitchComparisonResult, PitchDeviationPoint

def _fake_response(text):
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)])

def test_build_analysis_summary_includes_only_provided_categories():
    pitch_result = PitchComparisonResult(points=[
        PitchDeviationPoint(reference_time=1.0, student_time=1.0, reference_hz=440.0, student_hz=445.0, cents_deviation=30.0)
    ])
    summary = build_analysis_summary(pitch=pitch_result)
    assert "pitch" in summary
    assert "rhythm" not in summary

def test_build_analysis_summary_shapes_flagged_regions_correctly():
    dynamics_result = DynamicsComparisonResult(points=[
        DynamicsDeviationPoint(reference_time=2.0, student_time=2.0, reference_loudness_db=-20.0, student_loudness_db=-10.0, loudness_difference_db=10.0)
    ])
    summary = build_analysis_summary(dynamics=dynamics_result)
    assert summary["dynamics"]["mean_absolute_loudness_difference_db"] == 10.0
    assert summary["dynamics"]["flagged_regions"][0]["issue"] == "louder_than_reference"

def test_generate_feedback_empty_summary_skips_the_api_call():
    client = MagicMock()
    result = generate_feedback({}, client)
    assert result == []
    client.messages.create.assert_not_called()

def test_generate_feedback_parses_valid_response():
    client = MagicMock()
    client.messages.create.return_value = _fake_response(json.dumps([
        {"category": "pitch", "text": "Sharp by 30 cents around 0:42.", "timestamp_reference": 42.0}
    ]))
    summary = {"pitch": {"mean_absolute_cents_deviation": 30.0, "flagged_regions": []}}
    result = generate_feedback(summary, client)
    assert len(result) == 1
    assert result[0]["category"] == "pitch"
    client.messages.create.assert_called_once()

def test_generate_feedback_filters_invalid_categories():
    client = MagicMock()
    client.messages.create.return_value = _fake_response(json.dumps([
        {"category": "pitch", "text": "Valid item.", "timestamp_reference": None},
        {"category": "not_a_real_category", "text": "Should be dropped.", "timestamp_reference": None},
    ]))
    result = generate_feedback({"pitch": {}}, client)
    assert len(result) == 1
    assert result[0]["category"] == "pitch"

def test_generate_feedback_raises_on_invalid_json():
    client = MagicMock()
    client.messages.create.return_value = _fake_response("this is not json")
    with pytest.raises(ValueError):
        generate_feedback({"pitch": {}}, client)
