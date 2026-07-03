"""Unit tests for the QR Code Generator application.

These tests exercise the core behaviors of main.py: URL validation,
directory creation, and QR code image generation. They run locally with
``pytest`` and automatically in CI via the GitHub Actions workflow.
"""

from pathlib import Path

import pytest

import main


def test_is_valid_url_accepts_well_formed_url():
    """A syntactically valid http/https URL should pass validation."""
    assert main.is_valid_url("https://www.njit.edu") is True
    assert main.is_valid_url("https://www.youtube.com/@MattFeroz/videos") is True


def test_is_valid_url_rejects_malformed_url():
    """Strings that are not URLs should fail validation and return False."""
    assert main.is_valid_url("not-a-url") is False
    assert main.is_valid_url("htp:/broken") is False
    assert main.is_valid_url("") is False


def test_create_directory_creates_nested_path(tmp_path):
    """create_directory should create the directory tree, including parents."""
    target = tmp_path / "nested" / "qr_codes"
    main.create_directory(target)
    assert target.is_dir()


def test_create_directory_is_idempotent(tmp_path):
    """Calling create_directory on an existing directory should not raise."""
    target = tmp_path / "qr_codes"
    main.create_directory(target)
    main.create_directory(target)  # second call must succeed silently
    assert target.is_dir()


def test_generate_qr_code_writes_png_for_valid_url(tmp_path):
    """A valid URL should produce a non-empty PNG file at the given path."""
    output = tmp_path / "QRCode_test.png"
    main.generate_qr_code("https://www.njit.edu", output)
    assert output.is_file()
    # PNG files always begin with an 8-byte magic signature.
    assert output.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_generate_qr_code_skips_invalid_url(tmp_path):
    """An invalid URL should be rejected and no file should be written."""
    output = tmp_path / "QRCode_test.png"
    main.generate_qr_code("definitely not a url", output)
    assert not output.exists()


def test_generate_qr_code_honors_custom_colors(tmp_path):
    """Custom fill/background colors should still yield a valid PNG file."""
    output = tmp_path / "QRCode_colors.png"
    main.generate_qr_code("https://www.njit.edu", output,
                          fill_color="blue", back_color="yellow")
    assert output.is_file()
    assert output.stat().st_size > 0
