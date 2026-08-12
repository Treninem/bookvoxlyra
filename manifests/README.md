# BookVoxLyra manifests

`import_index.json` is the **only canonical discovery index** for VoxLyra GitHub Import.

Other files in this directory may preserve historical archive metadata, checksums or completed-work records from earlier preparation stages. They are not permission to import a package and they are not evidence that the binary payload is currently stored in this repository.

A package is eligible for VoxLyra discovery only when all of the following are true:

1. it has an entry in `import_index.json`;
2. that entry contains the boolean `"enabled": true`;
3. the package directory and its current `manifest.json` are present;
4. every file declared by that manifest is present;
5. every declared SHA-256 matches;
6. genuine source/licensing evidence required by the content type is present;
7. `python3 tools/validate_packages.py` succeeds.

Current legacy records with missing payloads stay `enabled: false`, even when an older catalog calls their source archive completed or import-ready. This prevents metadata-only records from being mistaken for deployable content.
