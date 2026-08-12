from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import validate_packages as validator


class PackageValidatorTests(unittest.TestCase):
    def _repository(self, *, checksum: str | None = None, enabled: object = True) -> tuple[Path, Path]:
        root = Path(tempfile.mkdtemp(prefix="bookvoxlyra-validator-"))
        package = root / "books" / "sample"
        package.mkdir(parents=True)
        payload = b"hello VoxLyra\n"
        (package / "book.txt").write_bytes(payload)
        actual = hashlib.sha256(payload).hexdigest()
        manifest = {
            "package_id": "sample",
            "content_type": "book",
            "title": "Sample",
            "language": "ru",
            "version": "1.0",
            "created_at": "2026-08-12T00:00:00Z",
            "files": ["book.txt"],
            "checksums": {"book.txt": checksum or actual},
        }
        (package / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False),
            encoding="utf-8",
        )
        manifests = root / "manifests"
        manifests.mkdir()
        index = {
            "schema_version": 1,
            "packages": [
                {
                    "path": "books/sample",
                    "manifest_path": "books/sample/manifest.json",
                    "enabled": enabled,
                }
            ],
        }
        index_path = manifests / "import_index.json"
        index_path.write_text(json.dumps(index), encoding="utf-8")
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
        return root, index_path

    def _validate(self, root: Path, index_path: Path):
        with patch.object(validator, "ROOT", root), patch.object(validator, "INDEX_PATH", index_path):
            return validator.validate()

    def test_valid_enabled_payload_checks_real_sha256(self):
        root, index_path = self._repository()
        self.assertEqual(self._validate(root, index_path), (1, 1))

    def test_corrupt_payload_checksum_is_rejected(self):
        root, index_path = self._repository(checksum="0" * 64)
        with self.assertRaisesRegex(validator.ValidationError, "SHA-256 mismatch"):
            self._validate(root, index_path)

    def test_enabled_must_be_boolean_not_truthy_text(self):
        root, index_path = self._repository(enabled="true")
        with self.assertRaisesRegex(validator.ValidationError, "enabled must be true or false"):
            self._validate(root, index_path)

    def test_undeclared_payload_file_is_rejected(self):
        root, index_path = self._repository()
        (root / "books" / "sample" / "stale.bin").write_bytes(b"stale")
        with self.assertRaisesRegex(validator.ValidationError, "undeclared package files"):
            self._validate(root, index_path)


if __name__ == "__main__":
    unittest.main()
