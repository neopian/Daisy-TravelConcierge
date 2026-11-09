import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("flutter_sdk", Path(__file__).resolve().parents[1] / "flutter_sdk.py")
sdk = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sdk)
PIN = {"version": "3.32.8", "revision": "pinned-commit", "repository": "https://github.com/flutter/flutter.git"}


class FlutterSdkTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.cache = self.root / "sdk cache"
        self.environ = patch.dict(os.environ, {}, clear=True)
        self.environ.start()
        self.addCleanup(self.environ.stop)

    def test_wrong_default_sdk_is_skipped(self):
        wrong, correct = self.root / "newer", self.root / "pinned"
        with patch.object(sdk, "candidates", return_value=[wrong, correct]), \
             patch.object(sdk, "revision", side_effect=["other", PIN["revision"]]), \
             patch.object(sdk, "install_sdk") as install:
            self.assertEqual(sdk.resolve_sdk(self.root, PIN, self.cache), correct)
            install.assert_not_called()

    def test_explicit_wrong_sdk_is_rejected(self):
        os.environ["FLUTTER_BIN"] = "custom-flutter"
        with patch.object(sdk, "sdk_from_command", return_value=self.root), \
             patch.object(sdk, "revision", return_value="other"):
            with self.assertRaisesRegex(RuntimeError, "FLUTTER_BIN"):
                sdk.resolve_sdk(self.root, PIN, self.cache)

    def test_offline_never_downloads_missing_sdk(self):
        os.environ["CONCIERGE_OFFLINE"] = "1"
        with patch.object(sdk, "candidates", return_value=[]), patch.object(sdk, "install_sdk") as install:
            with self.assertRaisesRegex(RuntimeError, "온라인"):
                sdk.resolve_sdk(self.root, PIN, self.cache)
            install.assert_not_called()

    def clone(self, command, **kwargs):
        self.assertEqual(command[1:7], ["clone", "--depth", "1", "--single-branch", "--branch", PIN["version"]])
        self.assertEqual(command[-2], PIN["repository"])
        destination = Path(command[-1])
        (destination / "bin").mkdir(parents=True)
        (destination / "bin/flutter").write_text("sdk fixture")
        return subprocess.CompletedProcess(command, 0)

    def test_install_verifies_commit_before_promoting_sdk(self):
        with patch.object(sdk.subprocess, "run", side_effect=self.clone), \
             patch.object(sdk, "revision", return_value=PIN["revision"]):
            result = sdk.install_sdk(PIN, self.cache)
        self.assertEqual(result, self.cache / PIN["version"])
        self.assertTrue((result / "bin/flutter").is_file())

    def test_mismatched_download_is_removed(self):
        with patch.object(sdk.subprocess, "run", side_effect=self.clone), \
             patch.object(sdk, "revision", return_value="unexpected"):
            with self.assertRaisesRegex(RuntimeError, "일치하지"):
                sdk.install_sdk(PIN, self.cache)
        self.assertEqual(list(self.cache.iterdir()), [])

    def test_existing_cache_is_not_overwritten(self):
        (self.cache / PIN["version"]).mkdir(parents=True)
        with patch.object(sdk.subprocess, "run") as clone:
            with self.assertRaisesRegex(RuntimeError, "캐시"):
                sdk.install_sdk(PIN, self.cache)
            clone.assert_not_called()

    def test_sdk_link_survives_project_rename_and_preserves_regular_folder(self):
        project = self.root / "original"
        project.mkdir()
        target = self.root / "shared sdk"
        target.mkdir()
        sdk.link_sdk(project, target)
        renamed = self.root / "새 프로젝트 with spaces"
        project.rename(renamed)
        self.assertEqual((renamed / ".tools/flutter").resolve(), target)
        sdk.link_sdk(renamed, target)
        (renamed / ".tools/flutter").unlink()
        (renamed / ".tools/flutter").mkdir()
        with self.assertRaisesRegex(RuntimeError, "덮어쓰지"):
            sdk.link_sdk(renamed, target)


if __name__ == "__main__":
    unittest.main()
