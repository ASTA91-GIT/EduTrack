import pytest
from backend.app.services import (
    classes_needed_to_reach,
    classes_can_miss,
    whatif_attendance,
    classify_risk,
)

def test_classes_needed_to_reach():
    assert classes_needed_to_reach(5, 10, 75.0) == 10
    assert classes_needed_to_reach(8, 10, 75.0) == 0
    assert classes_needed_to_reach(0, 0, 75.0) == 0

def test_classes_can_miss():
    assert classes_can_miss(9, 10, 75.0) == 2
    assert classes_can_miss(5, 10, 75.0) == 0

def test_whatif_attendance():
    assert whatif_attendance(5, 10, 5) == 66.67
    assert whatif_attendance(0, 0, 5) == 100.0

def test_classify_risk():
    assert classify_risk(80, 100, 75) == "SAFE"
    assert classify_risk(75, 100, 75) == "SAFE"
    assert classify_risk(74, 100, 75) == "AT_RISK"
    assert classify_risk(50, 100, 75) == "CRITICAL"
