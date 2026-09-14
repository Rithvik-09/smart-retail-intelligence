"""
Unit tests for crowd level classification module.
"""

from app.analytics.crowd import CrowdClassifier, CrowdLevel
from app.config import CrowdConfig


def test_crowd_classification_standard_thresholds():
    cfg = CrowdConfig(low=5, medium=10, high=20)
    classifier = CrowdClassifier(cfg)

    # 0 to 5 -> LOW
    assert classifier.classify(0) == CrowdLevel.LOW
    assert classifier.classify(3) == CrowdLevel.LOW
    assert classifier.classify(5) == CrowdLevel.LOW

    # 6 to 10 -> MEDIUM
    assert classifier.classify(6) == CrowdLevel.MEDIUM
    assert classifier.classify(10) == CrowdLevel.MEDIUM

    # 11 to 20 -> HIGH
    assert classifier.classify(11) == CrowdLevel.HIGH
    assert classifier.classify(20) == CrowdLevel.HIGH

    # 21+ -> CRITICAL
    assert classifier.classify(21) == CrowdLevel.CRITICAL
    assert classifier.classify(50) == CrowdLevel.CRITICAL


def test_custom_thresholds():
    # Store with smaller footprint
    cfg = CrowdConfig(low=2, medium=4, high=8)
    classifier = CrowdClassifier(cfg)

    assert classifier.classify(2) == CrowdLevel.LOW
    assert classifier.classify(3) == CrowdLevel.MEDIUM
    assert classifier.classify(7) == CrowdLevel.HIGH
    assert classifier.classify(9) == CrowdLevel.CRITICAL


def test_stats_dictionary():
    cfg = CrowdConfig(low=5, medium=10, high=20)
    classifier = CrowdClassifier(cfg)
    stats = classifier.get_stats(15)
    assert stats == {"crowdLevel": "HIGH"}
