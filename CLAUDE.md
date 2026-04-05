# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

```sh
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the game
python -m src.main

# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=src --cov-report=term-missing tests/

# Run unit tests only
pytest -m unit tests/

# Run integration tests only
pytest -m integration tests/

# Run a single test file
pytest tests/test_game_engine.py

# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Type checking
mypy src/
```

## Architecture

The game engine runs a command-driven loop that routes each player input through a sequential pipeline:

```
CommandParser.parse → GameEngine.process_command
                          ↳ WorldManager (navigation)
                          ↳ ChallengeFactory (challenge dispatch)
                          ↳ PlayerManager (state mutation)
                          ↳ UIController (display)
```

### Key packages

| Package | Role |
|---|---|
| `src/game/engine.py` | `GameEngine` owns the main game loop and coordinates all subsystems |
| `src/game/world.py` | `WorldManager` manages chamber graph, connections, and navigation |
| `src/game/player.py` | `PlayerManager` handles inventory, progress, and save/load delegation |
| `src/game/command_parser.py` | `CommandParser` lexes raw input into `ParsedCommand` / `CommandType` |
| `src/game/ui_controller.py` | `UIController` handles all display formatting and user-facing output |
| `src/game/map_renderer.py` | `MapRenderer` renders the ASCII labyrinth map |
| `src/challenges/` | Challenge system — `base.py` ABC, five concrete types, `factory.py` for dispatch |
| `src/config/game_config.py` | `GameConfig` loads and validates JSON configuration |
| `src/utils/data_models.py` | Core data types: `GameState`, `Item`, `Chamber`, etc. |
| `src/utils/save_load.py` | `SaveLoadManager` — serialises/deserialises game state to JSON |
| `src/utils/randomization.py` | Seeded randomisation for replayable labyrinth generation |
| `src/utils/exceptions.py` | `GameException`, `SaveLoadException`, etc. |

### Challenge types

| Type | Module |
|------|--------|
| Riddle | `src/challenges/riddle.py` |
| Puzzle | `src/challenges/puzzle.py` |
| Combat | `src/challenges/combat.py` |
| Skill test | `src/challenges/skill.py` |
| Memory game | `src/challenges/memory.py` |

All challenge types inherit from `ChallengeBase` in `src/challenges/base.py`.  
New challenge types must be registered in `src/challenges/factory.py`.

### Configuration

Config files are resolved in this order:
1. Path passed to `GameEngine(config_file=...)`
2. `game_config.json` (project root)
3. `config/game_config.json`
4. `~/.labrynth_config.json`

## Definition of Done

Every PR that ships a user-facing change **must** update all relevant surfaces before the PR is opened. Work through this checklist before pushing:

### CHANGELOG.md
- [ ] Entry added to `[Unreleased]` describing what changed

### ROADMAP.md
- [ ] If a planned milestone is completed: mark it ✓ and move it to the completed section

### Code surfaces (as applicable)
- [ ] `src/utils/data_models.py` — new data types or fields
- [ ] `src/config/game_config.py` — new config fields, validation rules, defaults
- [ ] `src/challenges/factory.py` — new challenge type registered
- [ ] `src/game/interfaces.py` — new interface methods

### Tests
- [ ] New functionality has unit tests covering the happy path and key error paths
- [ ] Integration tests updated if game flow or cross-system behaviour changed

### Docs
- [ ] `docs/` updated for new gameplay mechanics, configuration options, or commands
- [ ] `README.md` updated if the public-facing interface changed
