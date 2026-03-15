"""
Unit tests for qSOFA scoring engine.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models import Vitals
from app.qsofa import calculate_qsofa, get_risk_description


def _make_vitals(
    hr=80, spo2=98, temp=98.6, rr=16, sbp=120, gcs=15
) -> Vitals:
    return Vitals(
        heart_rate=hr,
        spo2=spo2,
        temperature_f=temp,
        respiratory_rate=rr,
        systolic_bp=sbp,
        gcs_score=gcs,
    )


def test_score_0_all_normal():
    v = _make_vitals(hr=75, rr=16, sbp=120, gcs=15)
    result = calculate_qsofa(v)
    assert result.score == 0
    assert result.risk_level == "low"
    assert not result.criteria.respiratory_rate_elevated
    assert not result.criteria.systolic_bp_low
    assert not result.criteria.altered_mental_status


def test_score_1_high_rr_only():
    v = _make_vitals(rr=24, sbp=120, gcs=15)
    result = calculate_qsofa(v)
    assert result.score == 1
    assert result.risk_level == "moderate"
    assert result.criteria.respiratory_rate_elevated
    assert not result.criteria.systolic_bp_low


def test_score_2_high_risk():
    v = _make_vitals(rr=24, sbp=90, gcs=15)
    result = calculate_qsofa(v)
    assert result.score == 2
    assert result.risk_level == "high"


def test_score_3_critical():
    v = _make_vitals(rr=28, sbp=85, gcs=12)
    result = calculate_qsofa(v)
    assert result.score == 3
    assert result.risk_level == "high"
    assert result.criteria.respiratory_rate_elevated
    assert result.criteria.systolic_bp_low
    assert result.criteria.altered_mental_status


def test_boundary_rr_22_triggers():
    v = _make_vitals(rr=22)
    result = calculate_qsofa(v)
    assert result.criteria.respiratory_rate_elevated is True


def test_boundary_rr_21_does_not_trigger():
    v = _make_vitals(rr=21)
    result = calculate_qsofa(v)
    assert result.criteria.respiratory_rate_elevated is False


def test_boundary_sbp_100_triggers():
    v = _make_vitals(sbp=100)
    result = calculate_qsofa(v)
    assert result.criteria.systolic_bp_low is True


def test_boundary_sbp_101_does_not_trigger():
    v = _make_vitals(sbp=101)
    result = calculate_qsofa(v)
    assert result.criteria.systolic_bp_low is False


def test_boundary_gcs_15_does_not_trigger():
    v = _make_vitals(gcs=15)
    result = calculate_qsofa(v)
    assert result.criteria.altered_mental_status is False


def test_boundary_gcs_14_triggers():
    v = _make_vitals(gcs=14)
    result = calculate_qsofa(v)
    assert result.criteria.altered_mental_status is True


def test_risk_descriptions():
    assert "Low" in get_risk_description(0)
    assert "Moderate" in get_risk_description(1)
    assert "HIGH" in get_risk_description(2)
    assert "CRITICAL" in get_risk_description(3)
