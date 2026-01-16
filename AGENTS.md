# Repository Guidelines

## Project Structure & Module Organization
- `sorawm/`: core package with `core.py` orchestrating detection/cleaning, `watermark_detector.py`, `watermark_cleaner.py`, `utils/` helpers, and `server/` FastAPI endpoints.
- `app.py` launches the Streamlit UI; `start_server.py` spins up the API service; `example.py` shows minimal CLI usage.
- `resources/` stores sample assets and downloaded weights; `outputs/` and `working_dir/` hold generated videos and intermediate artifacts; `train/` contains YOLO training and evaluation scripts.
- `data/`, `datasets/`, and `logs/` are scratch areas—keep large files out of Git and document new assets in `README.md`.

## Build, Test, and Development Commands
- `uv sync`: install Python 3.12 environment defined in `pyproject.toml`.
- `uv run streamlit run app.py`: launch the interactive watermark removal UI at `http://localhost:8501`.
- `uv run python start_server.py`: start the FastAPI service on port 5344 for programmatic access.
- `uv run python example.py`: run a quick end-to-end check using `resources/dog_vs_sam.mp4`.
- `uv run python train/train.py`: kick off YOLO fine-tuning; adjust dataset paths in `train/coco8.yaml` first.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation, descriptive snake_case identifiers, and upper camel case for classes (e.g., `SoraWM`).
- Preserve existing type hints and logging with `loguru.logger`; prefer explicit imports at module top.
- Add concise docstrings for new public functions and keep modules focused on a single responsibility.

## Testing Guidelines
- Place automated checks under `tests/` using `pytest`; name files `test_<module>.py` and target critical logic such as bbox interpolation and detector thresholds.
- Run `uv run pytest` before submitting; for model changes, add regression samples in `resources/` and document expected output metrics.
- Validate video-processing paths manually with `uv run python example.py` and attach hash or frame comparisons when altering pipelines.

## Commit & Pull Request Guidelines
- Use short imperative messages (e.g., `Fix detector bbox fill`) or the existing `Feature:` prefix convention; keep subject lines ≤72 characters.
- Break large work into focused commits and reference issues with `Fixes #<id>` where relevant.
- Pull requests should summarize motivation, list test commands executed, and include before/after frames or logs for detector/cleaner changes. Link datasets or new assets and highlight any migration steps.
