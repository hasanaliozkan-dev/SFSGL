# Changelog

## 0.2.0 (2026-10-28)

### Fixed
- Uploads with the same file name no longer overwrite each other. `add_ip_to_file` now works (it was accepted but ignored), and taken names get a `_1`, `_2`, ... suffix.
- Selecting several files uploaded only the first one; now every file is saved when `allow_multiple_upload` is on, and the picker only offers multiple selection then.
- `allow_multiple_upload=False` / `add_ip_to_file=True` crashed with `AttributeError`; real booleans are accepted alongside the old `"True"`/`"False"` strings.
- Uploading a file type that isn't allowed now shows an error instead of nothing.
- File names in Turkish and other non-ASCII scripts are kept (`çalışma.py` was saved as `calsma.py`, `作业.py` as `py`).
- The share page returned a 500 error when the shared folder didn't exist; it is now created.
- `FileGather` on its own saved uploads into `shared`, which the share page serves; the default is now `gathered`.
- Two simultaneous uploads from one IP could both pass the one-file limit.
- Cancelling the file picker on the upload page broke the form.
- `python -m SFSGL` works.
- Dockerfile: built from a wrong path and ran a missing `app.py`; submissions were lost with the container.

### Added
- Command-line options for folders, file types, ports, upload limit and the per-IP rule (`sfsgl --help`).
- Upload size limit, 50 MB by default (`max_upload_size_mb`, `--max-upload-mb`).
- `from SFSGL import SFSGL, FileGather, FileShare`.
- Tests and a GitHub Actions workflow for Python 3.9–3.13.

### Changed
- Requires Python 3.9 or newer.
- Build artifacts (`build/`, `dist/`, `*.egg-info`, `__pycache__`) are no longer tracked in git.
- Removed the unused Font Awesome font from the package.
- Removed the unused `SFSGL/requirements.txt` (its outdated `Flask==3.1.0` pin triggered a security alert; the package itself depends on `flask>=2.0`).

## 0.1.11 (2026-07-29)
- Latest release on PyPI before the changes above.
