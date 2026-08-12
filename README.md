# BookVoxLyra

Source-only repository for owner-controlled content import into VoxLyra.

VoxLyra does **not** use this repository as its database or permanent runtime storage. Packages are validated, downloaded selectively, imported through the existing VoxLyra pipeline, and temporary files are removed.

## Layout

- `books/<package_id>/` — EPUB/FB2/TXT/PDF and other supported book packages.
- `comics/<package_id>/` — comics, manga, manhwa and webtoon packages.
- `audiobooks/<package_id>/` — audiobook packages.
- `manifests/import_index.json` — repository-level import index for fast scans of large libraries.

## Import index

`manifests/import_index.json` is the preferred discovery path. It prevents VoxLyra from making an API request for every directory when the repository grows to hundreds or thousands of packages.

Each entry contains `path`, `manifest_path` and `enabled`. Disabled legacy/staging packages remain visible for provenance but are never offered for import. A package must not be enabled until its complete payload is actually committed.

## Canonical package manifest

Every **enabled** package must include `manifest.json` with at least:

```json
{
  "package_id": "example-book-001",
  "content_type": "book",
  "title": "Example",
  "language": "ru",
  "version": "1.0",
  "created_at": "2026-08-12T00:00:00Z",
  "files": [
    "metadata.json",
    "description.txt",
    "cover.jpg",
    "LICENSE.txt",
    "SOURCES.txt",
    "book.epub"
  ],
  "checksums": {
    "metadata.json": "<sha256>",
    "description.txt": "<sha256>",
    "cover.jpg": "<sha256>",
    "LICENSE.txt": "<sha256>",
    "SOURCES.txt": "<sha256>",
    "book.epub": "<sha256>"
  }
}
```

`content_type` is `book`, `comics` or `audiobook`. All paths are relative to the package directory and every declared file must have a real SHA-256 checksum.

Rights/source files such as `LICENSE.txt` and `SOURCES.txt` must contain real information and are never fabricated by the importer. Presence in GitHub does not itself grant redistribution rights.

## Current staging packages

The existing historical manifests currently have `payload_present=false` / `import_enabled=false`: their source archives are not stored in this repository. They are intentionally disabled in `manifests/import_index.json`, so VoxLyra will not treat them as importable packages or fail the whole scan because of an old manifest schema.

## Canonical-version rule

One work is stored only once and only under its latest canonical title and latest completed revision.

- Renaming a work does **not** create a new book.
- Old titles, old covers, superseded archives, intermediate stages and earlier revisions are not stored as separate importable works.
- When several archives belong to the same work, only the newest fully completed canonical package is eligible for import.
- Drafts, partial chapter ranges and working backups are excluded from the completed catalog.
