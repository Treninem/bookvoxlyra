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

A package remains `enabled: false` while any binary payload, final cover, manifest checksum or rights/source evidence is still missing. Metadata alone is never enough to make a work importable.

## Enabled package manifest

Every enabled package must contain a current VoxLyra import `manifest.json` with at least:

```json
{
  "package_id": "example-package",
  "content_type": "book",
  "title": "Example",
  "language": "ru",
  "version": "1.0",
  "created_at": "2026-08-13T00:00:00Z",
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
- every enabled package must explicitly declare both `LICENSE.txt` and `SOURCES.txt`;
- `LICENSE.txt` and `SOURCES.txt` must be non-empty UTF-8 text rather than placeholder files;
- an enabled package must contain an actual content payload in addition to metadata/cover/rights files;
- enabled package directories cannot contain undeclared payload files;
- duplicate enabled package IDs or duplicate index paths are rejected.

Rights/source files must contain real provenance and permission information and are never fabricated by the importer or validator. Structural validation does not itself invent or grant copyright permission; the source evidence still has to be genuine.

## Automatic validation

`.github/workflows/validate-packages.yml` runs on changes to package folders, the import index, validator or workflow itself.

It executes:

```bash
python3 tools/validate_packages.py
```

The repository remains valid with zero enabled packages. Once a real payload is committed and its index entry is switched to `enabled: true`, CI verifies the manifest, rights/source files, declared payload and SHA-256 values before VoxLyra can consume the package.

`validator-tests.yml` additionally verifies temporary fixture packages and confirms that corrupt hashes, ambiguous `enabled` values, missing/blank rights files and undeclared payload files are rejected.

## Recovered final books · 2026-08-13

Two real final source archives were recovered from the project owner's file library and independently inspected instead of relying only on historical metadata.

### `mezhdu-dvumya-otvetami-final`

- source archive: `VoxLyra_Import_Mezhdu_dvumya_otvetami_FINAL.zip`;
- source archive SHA-256: `8c30d355bde52302041a1866edf53a636d735a698a419dda98b546b875abe46f`;
- embedded FB2 SHA-256: `3bd7213a458fb20d26d2175594ad949e43000e3c75e2905c48a5751b9f8bcb24`;
- source cover SHA-256: `64706e708bda5979e698fff58f299aa2a5ad37ce794613118c9f8a213aa1088b`;
- package metadata and FB2 identify the author as `@Treninem`;
- chapter sequence verified as `1–1020`;
- metadata is normalized to VoxLyra `platform_original` + `rights_checked=true`;
- `LICENSE.txt` and `SOURCES.txt` provenance records are committed.

### `schastye-vo-mne-final`

- source archive: `VoxLyra_Import_Schastye_vo_mne_FINAL(1).zip`;
- source archive SHA-256: `ba01f38c06b76fd6a6bdf2806c18f5de8e321313151e4f4da2d1d00ba064d594`;
- embedded FB2 SHA-256: `b48a2e65d852b9f5a5ab705850865d038558182351ae649f18215e825a325393`;
- source cover SHA-256: `d6f1febb5a934c1b78dab85c75328e555be593920c26ff8322c16a80aa71842f`;
- package metadata and FB2 identify the author as `Treninem`;
- chapter sequence verified as `1–170`;
- metadata is normalized to VoxLyra `platform_original` + `rights_checked=true`;
- `LICENSE.txt` and `SOURCES.txt` provenance records are committed.

Both final FB2 texts were converted into standard EPUB payloads without changing chapter order or paragraph text, and source-ready package archives were retained in the project owner's file library. Their import-index entries intentionally remain disabled until the exact binary EPUB/cover bytes reach this repository in the same atomic package commit.

## Owner binary publication bridge

VoxLyra `v1.16.1` now contains a disabled-by-default `SYSTEM_OWNER_ID` source publisher designed for these prepared archives.

- Telegram command: `/github_source_publish`;
- hidden system-owner button: `⬆️ Source ZIP → GitHub` when enabled;
- separate fine-grained `GITHUB_SOURCE_WRITE_TOKEN` restricted to this source repository;
- validates ZIP structure, manifest, SHA-256, rights/source evidence and actual work payload;
- creates Git blobs first;
- atomically replaces the canonical package tree and switches this repository's import-index entry to `enabled=true` in the same commit;
- deletes stale files from a previous canonical package revision;
- fast-forwards the branch without force;
- an upload error before the ref update leaves the currently visible package/index untouched.

This gives binary source packages a controlled path into the repository without putting the write token in source control and without allowing regular admins/owners to publish content.

## Canonical-version rule

One work is stored only once and only under its latest canonical title and latest completed revision.

- Renaming a work does **not** create a new book.
- Old titles, old covers, superseded archives, intermediate stages and earlier revisions are not stored as separate importable works.
- When several archives belong to the same work, only the newest fully completed canonical package is eligible for import.
- Drafts, partial chapter ranges and working backups are excluded from the completed catalog.

## Current blocker

The two recovered books are no longer blocked by discovery, chapter integrity, rights-provenance staging or missing publication code. Their remaining production step is deployment configuration: the VoxLyra source-write bridge must be enabled with a separate fine-grained GitHub token (`Contents: Read and write`) and then each already prepared source-ready ZIP can be sent through the hidden system-owner flow. Until that write credential is configured, both index entries deliberately stay disabled and VoxLyra cannot import a half-package.
