import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run_eval import _provider_only_env, _prf


def test_provider_only_env_filters_to_allowed_keys(monkeypatch):
    monkeypatch.delenv("VLM_MODEL", raising=False)
    monkeypatch.setenv("NVIDIA_API_KEY", "nk")
    monkeypatch.setenv("GEMINI_API_KEY", "gk")
    monkeypatch.setenv("UNRELATED", "x")
    env = _provider_only_env(["NVIDIA_API_KEY", "VLM_MODEL"])
    assert env == {"NVIDIA_API_KEY": "nk"}


def test_provider_only_env_empty_when_key_absent(monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("VLM_MODEL", raising=False)
    env = _provider_only_env(["NVIDIA_API_KEY", "VLM_MODEL"])
    assert env == {}


def test_prf_perfect_match():
    assert _prf(2, 2) == (1.0, 1.0)


def test_prf_false_positive_lowers_precision():
    precision, recall = _prf(3, 1)
    assert precision < 1.0
    assert recall == 1.0
