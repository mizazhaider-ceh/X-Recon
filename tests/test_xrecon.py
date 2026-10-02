"""Tests for X-Recon core helpers. Only light deps (rich, colorama) are needed."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modules"))

from utils import _esc, _safe_filename, InputValidator, ResultSaver  # noqa: E402


class TestEscaping:
    def test_esc_html(self):
        assert _esc('<script>alert("x")</script>') == "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;"

    def test_esc_none(self):
        assert _esc(None) == ""

    def test_esc_plain(self):
        assert _esc("hello") == "hello"


class TestSafeFilename:
    def test_traversal_stripped(self):
        safe = _safe_filename("../../etc/passwd")
        assert "/" not in safe and "\\" not in safe

    def test_spaces_stripped(self):
        assert _safe_filename("exa mple.com") == "exa_mple.com"

    def test_normal_kept(self):
        assert _safe_filename("example.com") == "example.com"


class TestInputValidator:
    def test_valid_ip(self):
        assert InputValidator.validate_ip("192.168.1.1") is True

    def test_invalid_ip(self):
        assert InputValidator.validate_ip("999.1.1.1") is False
        assert InputValidator.validate_ip("example.com") is False

    def test_valid_domain(self):
        assert InputValidator.validate_domain("example.com") is True

    def test_invalid_domain(self):
        assert InputValidator.validate_domain("not a domain") is False

    def test_valid_port_range(self):
        ok, (s, e) = InputValidator.validate_port_range("1-100")
        assert ok and (s, e) == (1, 100)

    def test_invalid_port_range(self):
        ok, _ = InputValidator.validate_port_range("100-1")
        assert ok is False
        ok, _ = InputValidator.validate_port_range("abc")
        assert ok is False


class TestResultSaver:
    def test_report_escapes_untrusted_content(self, tmp_path, monkeypatch):
        saver = ResultSaver("testmod")
        monkeypatch.setattr(saver, "results_dir", str(tmp_path))
        html = saver._generate_html_report('evil"><h1>x', ['<script>alert(1)</script>'])
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
        assert 'evil"&gt;&lt;h1&gt;x' in html or "evil" in html

    def test_save_text_sanitizes_filename(self, tmp_path, monkeypatch):
        saver = ResultSaver("testmod")
        monkeypatch.setattr(saver, "results_dir", str(tmp_path))
        path = saver.save_text("../evil", ["line1"])
        assert path is not None
        assert os.path.dirname(path) == str(tmp_path)
        assert os.path.isfile(path)

    def test_save_json_sanitizes_filename(self, tmp_path, monkeypatch):
        saver = ResultSaver("testmod")
        monkeypatch.setattr(saver, "results_dir", str(tmp_path))
        path = saver.save_json("a/b", {"k": "v"})
        assert path is not None
        assert "/" not in os.path.basename(path)


class TestRunModule:
    def test_rejects_shell_metachars(self, capsys):
        import main as xrecon_main

        xrecon_main.run_module("port_scanner.py; rm -rf /")
        out = capsys.readouterr().out
        assert "Invalid module name" in out

    def test_rejects_path_traversal(self, capsys):
        import main as xrecon_main

        xrecon_main.run_module("../server/server.py")
        out = capsys.readouterr().out
        assert "Invalid module name" in out

    def test_missing_module_reported(self, capsys):
        import main as xrecon_main

        xrecon_main.run_module("nope.py")
        out = capsys.readouterr().out
        assert "Module not found" in out
