# BookVoxLyra

Source-only repository for owner-controlled content import into VoxLyra.

VoxLyra does **not** use this repository as its database or permanent runtime storage. Packages are validated, downloaded selectively, imported through the existing VoxLyra pipeline, and temporary files are removed.

## Layout

- `books/<package_id>/` — EPUB/FB2/TXT/PDF and other supported book packages.
- `comics/<package_id>/` — comics, manga, manhwa and webtoon packages.
- `audiobooks/<package_id>/` — audiobook packages.
- `manifests/` — optional repository-level indexes/manifests.

Every package must include `manifest.json`. Rights/source files such as `LICENSE.txt` and `SOURCES.txt` must contain real information and are never fabricated by the importer.
