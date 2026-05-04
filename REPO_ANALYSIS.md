# Repository Analysis: tail-tagger

## High-level purpose
Tail Tagger is a PySide6 desktop application for manual and AI-assisted image tagging using e621-compatible tags. It supports optional Joint Tagger Project classifiers and persists tagging state through per-folder staging workfiles. 

## Current architecture
- **UI orchestration** lives in `MainWindow` (`main.py`), which wires left/center/right panels, navigation, configuration loading, and startup dependency checks.
- **Tag state** is centralized in `TagListModel` + `TagData` and exposed to multiple synchronized panels.
- **Persistence + filesystem I/O** is consolidated in `FileOperations` (`file_operations.py`) with JSON helpers, workfile lifecycle, import/export behavior, and folder scanning.
- **Classifier pipeline** is encapsulated in `ClassifierManager` (`classifier_manager.py`) with model discovery, lazy model loading, inference worker dispatch, and Qt signal-based result delivery.
- **Bulk operations** are modularized under `tail_tagger/bulk_operations/` with a manager + dialogs, and backup-oriented safety behavior.

## Strengths
1. **Clear feature modularity**
   - UI panels, model management, and file operations are separated into focused modules.
2. **Graceful AI optionality**
   - The app remains usable for manual-only workflows; model usage is additive.
3. **Operational safety in bulk edits**
   - Explicit backup behavior and staged workfiles reduce destructive risk.
4. **Startup dependency gate**
   - `check_dependencies()` gives users actionable errors before expensive UI/model init.
5. **Asynchronous inference flow**
   - Threaded workers prevent UI freezes during model load and analysis.

## Risks / technical debt observed
1. **Very large `MainWindow` responsibility surface**
   - `main.py` handles startup checks, UI construction, navigation, persistence coordination, and multiple workflows. This may slow iteration and increase regression probability.
2. **`print`-driven observability**
   - Logging is mostly ad-hoc `print()` statements across core modules, limiting structured diagnostics and production debugging.
3. **File I/O and UI coupling**
   - `FileOperations.export_tags()` directly invokes dialogs and platform-specific opener calls; this constrains testability.
4. **Potential error-path inconsistency**
   - Some methods return default values while others only print errors; error handling conventions are not fully uniform.
5. **No explicit test suite surfaced at repo root**
   - No obvious automated tests discovered in current file listing, increasing reliance on manual verification.

## Recommended near-term improvements (highest ROI)
1. **Introduce structured logging**
   - Replace most `print` calls with Python `logging` (levels, module names, optional file logging).
2. **Split app bootstrap from UI composition**
   - Keep `main.py` thin by extracting startup checks, menu wiring, and panel composition into dedicated modules.
3. **Decouple UI prompts from file service layer**
   - Move QFileDialog/xdg-open behavior out of `FileOperations`; keep that class pure I/O/domain logic.
4. **Define consistent error contract**
   - Standardize when to raise, return defaults, and emit user-visible errors.
5. **Add a minimal test baseline**
   - Start with fast unit tests for `FileOperations` helpers and model discovery path behavior.

## Suggested roadmap
- **Phase 1 (stability):** logging + error contract + small `FileOperations` refactor
- **Phase 2 (maintainability):** `MainWindow` decomposition and controller/service boundaries
- **Phase 3 (quality):** unit tests + smoke test harness for launch and folder load

## Notes on analysis scope
This analysis is based on static review of repository documentation and representative core modules (`README.md`, `CLAUDE.md`, `main.py`, `file_operations.py`, `classifier_manager.py`).
