# BookVoxLyra

Source-only repository for owner-controlled content import into VoxLyra.

VoxLyra does **not** use this repository as its database or permanent runtime storage. Packages are validated, downloaded selectively, imported through the existing VoxLyra pipeline, and temporary files are removed.

## Layout

- `books/<package_id>/` — EPUB/FB2/TXT/PDF and other supported book packages.
- `comics/<package_id>/` — comics, manga, manhwa and webtoon packages.
- `audiobooks/<package_id>/` — audiobook packages.
- `manifests/import_index.json` — canonical package discovery index used by VoxLyra.
- `tools/validate_packages.py` — source-side structural/SHA-256 validator.

## Import index

`manifests/import_index.json` is the fast discovery entry point. Every entry contains a package `path` and can optionally specify `manifest_path`.

A package is considered importable only when its index entry has:

```json
{
  "path": "books/example-package",
  "manifest_path": "books/example-package/manifest.json",
  "enabled": true
}
```

Known legacy records whose payload is not actually stored in this repository stay `enabled: false`. Do **not** enable a package merely because metadata for an old archive exists.

## Enabled package manifest

Every enabled package must contain a current VoxLyra import `manifest.json` with at least:

```json
{
  "package_id": "example-package",
  "content_type": "book",
  "title": "Example",
  "language": "ru",
  "version": "1.0",
  "created_at": "2026-08-12T00:00:00Z",
  "files": [
    "metadata.json",
    "book.epub",
    "LICENSE.txt",
    "SOURCES.txt"
  ],
  "checksums": {
    "metadata.json": "<sha256>",
    "book.epub": "<sha256>",
    "LICENSE.txt": "<sha256>",
    "SOURCES.txt": "<sha256>"
  }
}
```

Rules enforced by the source validator and mirrored by VoxLyra:

- `package_id` is ASCII-safe and at most 51 characters so owner Telegram callbacks remain valid;
- `content_type` is `book`, `comics` or `audiobook` and must match the top-level package folder;
- payload paths must be relative and cannot contain `..`;
- `files` is non-empty, unique and capped at 20,000 entries;
- `checksums` must match `files` exactly;
- every declared file must exist and match its SHA-256;
- enabled package directories cannot contain undeclared payload files;
- duplicate enabled package IDs or duplicate index paths are rejected.

Rights/source files such as `LICENSE.txt` and `SOURCES.txt` must contain real information and are never fabricated by the importer or validator.

## Automatic validation

`.github/workflows/validate-packages.yml` runs on changes to package folders, the import index, validator or workflow itself.

It executes:

```bash
python3 tools/validate_packages.py
```

The current repository is valid even when it has zero enabled packages. Once a real payload is uploaded and its index entry is switched to `enabled: true`, CI immediately verifies the manifest, declared files and SHA-256 values before VoxLyra can consume the package.

## Canonical-version rule

One work is stored only once and only under its latest canonical title and latest completed revision.

- Renaming a work does **not** create a new book.
- Old titles, old covers, superseded archives, intermediate stages and earlier revisions are not stored as separate importable works.
- When several archives belong to the same work, only the newest fully completed canonical package is eligible for import.
- Drafts, partial chapter ranges and working backups are excluded from the completed catalog.

## Current blocker

The existing recorded packages are intentionally disabled because their original binary payloads are not present in this repository. Their metadata may describe checked historical archives, but metadata alone is not importable content. A package must remain disabled until the real payload, manifest checksums and genuine rights/source evidence are present.
