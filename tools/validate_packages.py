from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "manifests" / "import_index.json"
PACKAGE_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,51}$")
TYPE_DIRS = {"book": "books", "comics": "comics", "audiobook": "audiobooks"}
MAX_PACKAGES = 5000
MAX_FILES = 20_000


class ValidationError(RuntimeError):
    pass


def _safe_relative(value: object, *, label: str) -> str:
    raw = str(value or "").strip().strip("/")
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or ".." in path.parts or str(path) in {"", "."}:
        raise ValidationError(f"unsafe {label}: {value!r}")
    return str(path)


def _load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON: {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"JSON root must be an object: {path.relative_to(ROOT)}")
    return data


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_enabled_package(entry: dict, seen_ids: set[str]) -> tuple[str, int]:
    package_path = _safe_relative(entry.get("path"), label="package path")
    manifest_path = str(entry.get("manifest_path") or f"{package_path}/manifest.json")
    manifest_path = _safe_relative(manifest_path, label="manifest path")
    package_dir = (ROOT / package_path).resolve()
    manifest_file = (ROOT / manifest_path).resolve()
    if not package_dir.is_relative_to(ROOT.resolve()) or not manifest_file.is_relative_to(ROOT.resolve()):
        raise ValidationError(f"path escapes repository: {package_path}")
    if not package_dir.is_dir():
        raise ValidationError(f"missing package directory: {package_path}")
    if manifest_file.parent != package_dir:
        raise ValidationError(f"manifest must live in package root: {manifest_path}")

    manifest = _load_json(manifest_file)
    required = {
        "package_id", "content_type", "title", "language", "version",
        "created_at", "files", "checksums",
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise ValidationError(f"{manifest_path}: missing fields: {', '.join(missing)}")

    package_id = str(manifest["package_id"]).strip()
    if not PACKAGE_ID_RE.fullmatch(package_id):
        raise ValidationError(f"{manifest_path}: invalid package_id")
    if package_id in seen_ids:
        raise ValidationError(f"duplicate enabled package_id: {package_id}")
    seen_ids.add(package_id)

    content_type = str(manifest["content_type"]).strip().lower()
    if content_type not in TYPE_DIRS:
        raise ValidationError(f"{manifest_path}: invalid content_type: {content_type}")
    expected_prefix = TYPE_DIRS[content_type] + "/"
    if not package_path.startswith(expected_prefix):
        raise ValidationError(
            f"{manifest_path}: content_type={content_type} does not match path {package_path}"
        )

    title = str(manifest["title"]).strip()
    language = str(manifest["language"]).strip()
    version = str(manifest["version"]).strip()
    created_at = str(manifest["created_at"]).strip()
    if not title or len(title) > 500:
        raise ValidationError(f"{manifest_path}: invalid title")
    if not language or len(language) > 32:
        raise ValidationError(f"{manifest_path}: invalid language")
    if not version or len(version) > 128:
        raise ValidationError(f"{manifest_path}: invalid version")
    if not created_at or len(created_at) > 128:
        raise ValidationError(f"{manifest_path}: invalid created_at")

    files = manifest["files"]
    checksums = manifest["checksums"]
    if not isinstance(files, list) or not files or len(files) > MAX_FILES:
        raise ValidationError(f"{manifest_path}: files must contain 1..{MAX_FILES} entries")
    if not isinstance(checksums, dict):
        raise ValidationError(f"{manifest_path}: checksums must be an object")

    normalized_files = [_safe_relative(item, label="payload path") for item in files]
    if len(normalized_files) != len(set(normalized_files)):
        raise ValidationError(f"{manifest_path}: duplicate files entries")
    normalized_checksums = {
        _safe_relative(key, label="checksum path"): str(value).strip().lower()
        for key, value in checksums.items()
    }
    if set(normalized_checksums) != set(normalized_files):
        raise ValidationError(f"{manifest_path}: checksums keys must exactly match files")

    for relative in normalized_files:
        expected = normalized_checksums[relative]
        if not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValidationError(f"{manifest_path}: invalid SHA-256 for {relative}")
        payload = (package_dir / relative).resolve()
        if not payload.is_relative_to(package_dir):
            raise ValidationError(f"{manifest_path}: payload escapes package: {relative}")
        if not payload.is_file():
            raise ValidationError(f"{manifest_path}: missing payload: {relative}")
        actual = _sha256(payload)
        if actual != expected:
            raise ValidationError(
                f"{manifest_path}: SHA-256 mismatch for {relative}: expected {expected}, got {actual}"
            )

    declared = set(normalized_files)
    actual_files = {
        path.relative_to(package_dir).as_posix()
        for path in package_dir.rglob("*")
        if path.is_file() and path.resolve() != manifest_file
    }
    extras = sorted(actual_files - declared)
    if extras:
        shown = ", ".join(extras[:10])
        suffix = f" (+{len(extras) - 10} more)" if len(extras) > 10 else ""
        raise ValidationError(f"{manifest_path}: undeclared package files: {shown}{suffix}")

    return package_id, len(normalized_files)


def validate() -> tuple[int, int]:
    index = _load_json(INDEX_PATH)
    packages = index.get("packages")
    if not isinstance(packages, list):
        raise ValidationError("manifests/import_index.json: packages must be a list")
    if len(packages) > MAX_PACKAGES:
        raise ValidationError(f"import index exceeds {MAX_PACKAGES} packages")

    seen_paths: set[str] = set()
    seen_ids: set[str] = set()
    enabled_count = 0
    payload_file_count = 0
    for number, entry in enumerate(packages, start=1):
        if not isinstance(entry, dict):
            raise ValidationError(f"import index entry #{number} must be an object")
        package_path = _safe_relative(entry.get("path"), label=f"entry #{number} path")
        if package_path in seen_paths:
            raise ValidationError(f"duplicate package path in import index: {package_path}")
        seen_paths.add(package_path)
        if entry.get("enabled") is not True:
            continue
        _, file_count = _validate_enabled_package(entry, seen_ids)
        enabled_count += 1
        payload_file_count += file_count
    return enabled_count, payload_file_count


def main() -> int:
    try:
        enabled, files = validate()
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        f"BookVoxLyra validation passed: {enabled} enabled package(s), "
        f"{files} declared payload file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
