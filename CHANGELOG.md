# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-04-05

### Fixed
- Win condition now triggers on completing the exit chamber (chamber 13 — Throne of Victory)
  rather than requiring all 13 chambers, making the game finishable
- Failed challenges no longer become permanent damage traps: after exhausting attempts, the
  challenge stays live and accepts answers — each wrong attempt costs HP rather than locking
  the player out forever
- Memory challenges correctly reset to the presentation phase after max attempts so the
  player can study the sequence and retry

### Added
- `exit_chamber` field in labyrinth config (`config/full_labyrinth.json`) — defaults to the
  highest chamber ID if omitted, making it portable to custom configs
- Challenge prompts now tell the player how to respond and that 'hint' is available
- GitHub Actions CI workflow (lint, type-check, test with coverage gate at 80%)
- GitHub Actions release workflow using python-semantic-release
- `requirements-dev.txt` with dev toolchain (ruff, mypy, pytest, semantic-release)
- `pyproject.toml` now has `[project]` and `[tool.semantic_release]` sections

## [0.1.0] - 2025-08-21

### Added
- Initial release of Labyrinth Adventure Game
- Text-based navigation through 13 interconnected chambers
- Five challenge types: riddles, puzzles, combat, skill tests, memory games
- Configurable victory flag system for CTF and educational use
- Progress tracking with inventory management
- Save/load system for persistent game state
- Randomised elements for replayable gameplay
- Docker/Podman container support
- Flag management scripts

[Unreleased]: https://github.com/lewta/Labrynth/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/lewta/Labrynth/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/lewta/Labrynth/releases/tag/v0.1.0
