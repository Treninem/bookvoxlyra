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

A package is importable only when its `manifests/import_index.json` record has `enabled: true`. A package remains disabled while any real payload, final cover, manifest checksum or rights/source evidence is missing. Metadata alone is never enough.

For enabled packages the source validator enforces safe package IDs/paths, type/path agreement, a maximum of 20,000 declared files, exact `files`/`checksums` agreement, SHA-256 verification, mandatory non-empty UTF-8 `LICENSE.txt` and `SOURCES.txt`, an actual work payload beyond metadata/cover/evidence files, no undeclared payload files and no duplicate enabled IDs/paths.

Rights/source files must contain genuine provenance and permission information. Structural validation never invents or grants copyright permission.

## Automatic validation

`.github/workflows/validate-packages.yml` runs `python3 tools/validate_packages.py`. `validator-tests.yml` separately verifies corrupt hashes, invalid `enabled` values, missing/blank rights files and undeclared payload rejection.

The repository is valid with zero enabled packages. An entry is switched to `enabled=true` only when its actual payload and exact checksums are present.

## Recovered final books · 2026-08-13

Two real final source archives were recovered from the project owner's file library and inspected from their actual bytes.

### `gran-realnosti-final` — «Грань реальности»

This is the same work that the recovered historical source archive called **«Между двумя ответами»**. The project owner later explicitly renamed the book to **«Грань реальности»** and requested a replacement cover. The later canonical cover was recovered from the same project-owner library, and an existing VoxLyra screenshot also shows the book under the later title. The old title is therefore treated only as provenance, not as a second book.

- canonical title: `Грань реальности`;
- previous title: `Между двумя ответами`;
- author: `@Treninem`;
- verified chapters: `1–1020`;
- historical source archive: `VoxLyra_Import_Mezhdu_dvumya_otvetami_FINAL.zip`;
- historical source archive SHA-256: `8c30d355bde52302041a1866edf53a636d735a698a419dda98b546b875abe46f`;
- source FB2 SHA-256: `3bd7213a458fb20d26d2175594ad949e43000e3c75e2905c48a5751b9f8bcb24`;
- canonical replacement cover SHA-256: `e091b0973dd892c90ff8c482d4c5585af1b88e38ced62b95bb1dac6079b168ec`;
- prepared EPUB SHA-256: `eaf4db6fece873ec067e66fa985619114bebdeabf48aadc790389a1882416e78`;
- source-ready ZIP: `gran-realnosti-final.source-ready.zip`;
- source-ready ZIP SHA-256: `341764d7e150dcdb5d4a05166995c180326159492b3671ea7e66f216966a97a3`;
- metadata classification: `platform_original`, `rights_checked=true`.

The EPUB publication metadata and head title were changed to `Грань реальности`; chapter order and paragraph text were not rewritten as part of the rename.

### `schastye-vo-mne-final` — «Счастье во мне»

- source archive: `VoxLyra_Import_Schastye_vo_mne_FINAL(1).zip`;
- source archive SHA-256: `ba01f38c06b76fd6a6bdf2806c18f5de8e321313151e4f4da2d1d00ba064d594`;
- embedded FB2 SHA-256: `b48a2e65d852b9f5a5ab705850865d038558182351ae649f18215e825a325393`;
- author: `Treninem`;
- verified chapters: `1–170`;
- metadata classification: `platform_original`, `rights_checked=true`.

Both source-ready package archives are retained in the project owner's file library. Their import-index entries remain disabled until their exact binary EPUB/cover bytes are physically committed to this repository.

## Owner binary publication bridge

VoxLyra `v1.16.1` contains a disabled-by-default `SYSTEM_OWNER_ID` source publisher for prepared source-ready ZIPs.

- command: `/github_source_publish`;
- hidden system-owner button: `⬆️ Source ZIP → GitHub` when enabled;
- separate fine-grained `GITHUB_SOURCE_WRITE_TOKEN`, restricted to this source repository;
- verifies ZIP structure, manifest, SHA-256, evidence files and actual payload;
- creates Git blobs before publication;
- atomically replaces a package tree and flips its index entry to `enabled=true` in the same commit;
- deletes stale files from the previous canonical package revision;
- fast-forwards without force;
- failures before ref update leave the visible repository/index unchanged.

## Canonical-version rule

One work is stored once under its latest canonical title and completed revision.

- Renaming does **not** create a second book.
- Old titles, old covers, superseded archives, intermediate stages and earlier revisions are not separate importable works.
- When several archives belong to one work, only the latest completed canonical package is eligible.
- Drafts and partial chapter ranges are excluded from the completed catalog.

## Current blocker

For «Грань реальности» the canonical rename, final cover, 1–1020 chapter integrity, EPUB conversion, source-ready manifest/checksums and rights/source provenance are now prepared. The remaining production step is placing the exact binary `book.epub` and `cover.png` bytes into `books/gran-realnosti-final/` and then enabling that index entry atomically. «Счастье во мне» has the same binary-placement step remaining.
