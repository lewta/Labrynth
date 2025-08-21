# Labyrinth Adventure Game

A Python command-line text-based adventure game where players navigate through a network of 13 interconnected chambers, each containing unique challenges that must be overcome to progress and ultimately escape the labyrinth.

## Features

- **Text-based Navigation**: Explore interconnected chambers through intuitive commands
- **5 Challenge Types**: Riddles, puzzles, combat, skill tests, and memory games
- **Configurable Victory Flag**: Customizable flag content and victory messages for different contexts
- **Progress Tracking**: Inventory management and game state persistence
- **Save/Load System**: Continue your adventure across sessions
- **Replayable Gameplay**: Randomized elements for multiple playthroughs

## Quick Start

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd labrynth
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the game:
   ```bash
   python -m src.main
   ```

### Basic Gameplay

- Use directional commands (`north`, `south`, `east`, `west`) to navigate
- Type `help` for available commands
- Complete challenges in each chamber to progress
- Collect items and manage your inventory
- Save your progress with the `save` command

## Victory Flag Configuration

The game features a configurable victory flag system perfect for CTF competitions, educational challenges, and themed events.

### Quick Flag Setup

```bash
# Create sample configuration
python scripts/manage_flag.py sample

# Update flag content
python scripts/manage_flag.py update "YOUR_CUSTOM_FLAG_2024"

# Test configuration
python scripts/manage_flag.py test
```

### Example Configurations

**CTF Competition:**
```json
{
  "victory": {
    "flag_content": "cyber_challenge_2024_winner",
    "flag_prefix": "CTF{",
    "flag_suffix": "}",
    "prize_message": "🏆 VICTORY ACHIEVED!\n\nYour CTF flag: {flag}"
  }
}
```

**Educational Challenge:**
```json
{
  "victory": {
    "flag_content": "PYTHON_MAZE_SOLVED",
    "flag_prefix": "CHALLENGE[",
    "flag_suffix": "]",
    "prize_message": "🎓 Excellent work!\n\nCompletion code: {flag}"
  }
}
```

For complete configuration documentation, see [docs/FLAG_CONFIGURATION.md](docs/FLAG_CONFIGURATION.md).

## Project Structure

```
├── src/                    # Source code
│   ├── main.py            # Entry point
│   ├── game/              # Core game logic
│   ├── challenges/        # Challenge system
│   ├── config/            # Configuration management
│   └── utils/             # Utility functions
├── tests/                 # Test suite
├── config/                # Configuration files
├── docs/                  # Documentation
├── scripts/               # Management scripts
└── data/                  # Game data and saves
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_game_engine.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Container Deployment

The game can be containerized using Docker/Podman:

```bash
# Build container
docker build -t labrynth .

# Run container
docker run -it labrynth
```

## Configuration

### Game Settings

Configuration files are searched in this order:
1. `game_config.json` (project root)
2. `config/game_config.json` (config directory)
3. `~/.labrynth_config.json` (user home)

### Available Settings

- **Victory Flag**: Customize flag content, format, and victory message
- **Game Display**: Adjust screen width and border characters
- **Challenge Settings**: Configure difficulty and randomization
- **Save System**: Control save file locations and formats

## Use Cases

### CTF Competitions
- Customizable flags for different competition tracks
- Themed victory messages for branding
- Easy flag rotation between events

### Educational Settings
- Custom completion codes for student verification
- Instructor-friendly flag formats
- Progress tracking for classroom use

### Corporate Training
- Team-building exercise with custom achievement codes
- Branded victory messages for company events
- Scalable for multiple teams or departments

### Gaming Events
- Themed flags for special occasions (Halloween, holidays)
- Social media-friendly victory messages
- Memorable completion rewards

## Management Scripts

### Flag Management
```bash
# Show current configuration
python scripts/manage_flag.py show

# Update flag content
python scripts/manage_flag.py update "NEW_FLAG"

# Change flag format
python scripts/manage_flag.py format --prefix "CTF{" --suffix "}"

# Update victory message
python scripts/manage_flag.py message "Your prize: {flag}"
```

### Game Administration
```bash
# Reset game state
python scripts/reset_game.py

# Backup save files
python scripts/backup_saves.py

# Generate game statistics
python scripts/game_stats.py
```

## Architecture

The game follows object-oriented design principles with clear separation of concerns:

- **Game Engine**: Core game loop and state management
- **World Manager**: Chamber navigation and connections
- **Player Manager**: Inventory, progress, and save/load
- **Challenge System**: Extensible challenge types with factory pattern
- **Configuration System**: Flexible JSON-based configuration
- **UI Controller**: Display formatting and user interaction

## Testing

Comprehensive test suite covering:
- Unit tests for all core components
- Integration tests for game flow
- Configuration system tests
- Challenge type validation
- Save/load functionality
- Flag management scripts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints for new functions
- Include docstrings for public methods
- Write tests for new features
- Update documentation as needed

## License

[Add your license information here]

## Support

- **Documentation**: See `docs/` directory for detailed guides
- **Issues**: Report bugs and feature requests via GitHub issues
- **Configuration Help**: See [docs/FLAG_CONFIGURATION.md](docs/FLAG_CONFIGURATION.md)
- **Development**: Check `docs/DEVELOPMENT.md` for setup instructions

---

*Escape the labyrinth, claim your victory flag!* 🏆