# BookVoxLyra

Source-only repository for owner-controlled content import into VoxLyra.

VoxLyra does **not** use this repository as its database or permanent runtime storage. Packages are validated, downloaded selectively, imported through the existing VoxLyra pipeline, and temporary files are removed.

## Layout

- `books/<package_id>/` — EPUB/FB2/TXT/PDF and other supported book packages.
- `comics/<package_id>/` — comics, manga, manhwa and webtoon packages.
- `audiobooks/<package_id>/` — audiobook packages.
- `manifests/` — optional repository-level indexes/manifests.

Every package must include `manifest.json`. Rights/source files such as `LICENSE.txt` and `SOURCES.txt` must contain real information and are never fabricated by the importer.

## Canonical-version rule

One work is stored only once and only under its latest canonical title and latest completed revision.

- Renaming a work does **not** create a new book.
- Old titles, old covers, superseded archives, intermediate stages and earlier revisions are not stored as separate importable works.
- When several archives belong to the same work, only the newest fully completed canonical package is eligible for import.
- Drafts, partial chapter ranges and working backups are excluded from the completed catalog.
