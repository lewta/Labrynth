# Victory Flag Configuration Guide

## Overview

The Labyrinth Adventure Game features a configurable victory flag system that allows administrators to customize the flag content, format, and victory message without modifying code. This guide covers all aspects of flag configuration, management, and troubleshooting.

## Quick Start

### Default Configuration

By default, the game uses the flag `FLAG{LABYRINTH_MASTER_2024}` with a standard victory message. No configuration is required for basic usage.

### Creating Your First Custom Flag

1. Run the flag management script to create a sample configuration:
   ```bash
   python scripts/manage_flag.py sample
   ```

2. Update the flag content:
   ```bash
   python scripts/manage_flag.py update "MY_CUSTOM_FLAG_2024"
   ```

3. Test your configuration:
   ```bash
   python scripts/manage_flag.py test
   ```

## Configuration File Format

### File Locations

The system searches for configuration files in the following order:
1. `game_config.json` (project root)
2. `config/game_config.json` (config directory)
3. `~/.labrynth_config.json` (user home directory)

### Complete Configuration Structure

```json
{
  "victory": {
    "flag_content": "LABYRINTH_MASTER_2024",
    "flag_prefix": "FLAG{",
    "flag_suffix": "}",
    "prize_message": "🏆 YOUR PRIZE: {flag}\n\nYou have proven yourself worthy of the ancient secrets!"
  },
  "game": {
    "title": "Labyrinth Adventure Game",
    "version": "1.0"
  },
  "display": {
    "width": 80,
    "border_char": "="
  }
}
```

### Victory Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `flag_content` | string | `"LABYRINTH_MASTER_2024"` | The main content of the flag |
| `flag_prefix` | string | `"FLAG{"` | Text that appears before the flag content |
| `flag_suffix` | string | `"}"` | Text that appears after the flag content |
| `prize_message` | string | See default message | Victory message template with `{flag}` placeholder |

## Flag Management Commands

### Basic Commands

#### Show Current Configuration
```bash
python scripts/manage_flag.py show
```
Displays the current flag configuration including the complete flag and victory message.

#### Update Flag Content
```bash
python scripts/manage_flag.py update "NEW_FLAG_CONTENT"
```
Updates only the flag content while preserving prefix, suffix, and message format.

#### Preview Flag Display
```bash
python scripts/manage_flag.py test
```
Shows how the flag will appear in the actual victory screen.

### Advanced Commands

#### Update Flag Format
```bash
# Change both prefix and suffix
python scripts/manage_flag.py format --prefix "CTF{" --suffix "}"

# Change only prefix
python scripts/manage_flag.py format --prefix "CHALLENGE{"

# Change only suffix  
python scripts/manage_flag.py format --suffix "]"
```

#### Update Victory Message
```bash
python scripts/manage_flag.py message "🎉 Congratulations! Your flag is: {flag}"
```
**Note:** The message template must contain the `{flag}` placeholder.

#### Create Sample Configuration
```bash
python scripts/manage_flag.py sample
```
Creates a sample configuration file with comments explaining all options.

## Configuration Examples

### CTF Competition Format
```json
{
  "victory": {
    "flag_content": "cyber_challenge_2024_winner",
    "flag_prefix": "CTF{",
    "flag_suffix": "}",
    "prize_message": "🏆 VICTORY ACHIEVED!\n\nYour CTF flag: {flag}\n\nSubmit this flag to claim your points!"
  }
}
```
**Result:** `CTF{cyber_challenge_2024_winner}`

### Educational Challenge Format
```json
{
  "victory": {
    "flag_content": "PYTHON_MAZE_SOLVED",
    "flag_prefix": "CHALLENGE[",
    "flag_suffix": "]",
    "prize_message": "🎓 Excellent work, student!\n\nYour completion code: {flag}\n\nShow this to your instructor for credit."
  }
}
```
**Result:** `CHALLENGE[PYTHON_MAZE_SOLVED]`

### Themed Event Format
```json
{
  "victory": {
    "flag_content": "HALLOWEEN_HORROR_ESCAPE_2024",
    "flag_prefix": "🎃SPOOKY{",
    "flag_suffix": "}👻",
    "prize_message": "🎃 You've escaped the haunted labyrinth! 👻\n\nYour Halloween prize: {flag}\n\nShare your victory with #HalloweenMaze!"
  }
}
```
**Result:** `🎃SPOOKY{HALLOWEEN_HORROR_ESCAPE_2024}👻`

### Corporate Training Format
```json
{
  "victory": {
    "flag_content": "TEAM_BUILDING_SUCCESS_Q4_2024",
    "flag_prefix": "ACME_CORP{",
    "flag_suffix": "}",
    "prize_message": "🏢 Congratulations, team member!\n\nYour achievement code: {flag}\n\nPresent this to HR for your team-building certificate."
  }
}
```
**Result:** `ACME_CORP{TEAM_BUILDING_SUCCESS_Q4_2024}`

### Minimalist Format
```json
{
  "victory": {
    "flag_content": "WINNER",
    "flag_prefix": "",
    "flag_suffix": "",
    "prize_message": "You won! Code: {flag}"
  }
}
```
**Result:** `WINNER`

## Integration with Game

### How Configuration is Loaded

1. **Startup:** Configuration is loaded when the game starts
2. **Caching:** Settings are cached in memory for performance
3. **Fallback:** If configuration fails, default values are used
4. **Updates:** Changes via management script take effect immediately

### Display Integration

The victory flag appears in the game's victory screen when a player completes all challenges. The configured message template is used with the complete flag substituted for the `{flag}` placeholder.

### Backward Compatibility

- Existing save games work with new flag configurations
- Default behavior matches the original hardcoded flag
- All existing tests continue to pass with default settings

## Troubleshooting

### Common Issues

#### Configuration File Not Found
**Symptoms:** Game uses default flag despite creating configuration file
**Solutions:**
1. Check file location - ensure it's in project root, config/, or home directory
2. Verify filename is exactly `game_config.json`
3. Run `python scripts/manage_flag.py sample` to create in correct location

#### Invalid JSON Format
**Symptoms:** Game shows warning about invalid configuration
**Solutions:**
1. Validate JSON syntax using online JSON validator
2. Check for missing commas, quotes, or brackets
3. Recreate file using `python scripts/manage_flag.py sample`

#### Flag Not Updating
**Symptoms:** Changes don't appear in game
**Solutions:**
1. Restart the game after configuration changes
2. Verify configuration file is in correct location
3. Check file permissions (must be readable)
4. Use `python scripts/manage_flag.py show` to verify current settings

#### Victory Message Template Errors
**Symptoms:** Default message appears despite custom template
**Solutions:**
1. Ensure template contains `{flag}` placeholder
2. Check for typos in placeholder (case-sensitive)
3. Verify JSON string escaping for special characters

#### Permission Errors
**Symptoms:** Cannot save configuration changes
**Solutions:**
1. Check file and directory permissions
2. Ensure user has write access to configuration directory
3. Try creating configuration in user home directory instead

### Advanced Troubleshooting

#### Debug Configuration Loading
```bash
# Check which configuration file is being used
python -c "from src.config.game_config import GameConfig; config = GameConfig(); print(f'Config file: {config._config_file}')"

# Verify configuration values
python scripts/manage_flag.py show
```

#### Test Configuration Parsing
```bash
# Validate JSON syntax
python -m json.tool game_config.json

# Test configuration loading
python -c "from src.config.game_config import GameConfig; GameConfig().load_config()"
```

#### Reset to Defaults
```bash
# Remove configuration file to use defaults
rm game_config.json config/game_config.json ~/.labrynth_config.json

# Or create fresh sample configuration
python scripts/manage_flag.py sample
```

### Error Messages and Solutions

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Configuration file not found" | Missing config file | Normal - defaults will be used |
| "Invalid JSON in configuration" | Malformed JSON | Fix JSON syntax or recreate file |
| "Missing {flag} placeholder" | Invalid message template | Add `{flag}` to message template |
| "Permission denied" | File access issues | Check file permissions |
| "Configuration key not found" | Missing config section | Add missing keys or use sample |

## Best Practices

### Security Considerations
- Flag content may be sensitive - protect configuration files appropriately
- Consider file permissions in multi-user environments
- Backup configuration files before making changes

### Performance Tips
- Configuration is loaded once at startup - no performance impact during gameplay
- Large message templates don't affect game performance
- File I/O only occurs during explicit save operations

### Deployment Recommendations
- Include configuration files in deployment packages
- Use environment-specific configuration files for different deployments
- Document custom configurations for team members
- Test configuration changes in development environment first

### Maintenance Guidelines
- Keep configuration files under version control
- Document custom flag formats for future reference
- Regularly backup configuration files
- Test configuration changes before production deployment

## API Reference

### GameConfig Class Methods

```python
from src.config.game_config import GameConfig

# Initialize with default or custom config file
config = GameConfig()  # Uses default search order
config = GameConfig("custom_config.json")  # Uses specific file

# Get complete flag
flag = config.get_victory_flag()  # Returns "FLAG{LABYRINTH_MASTER_2024}"

# Get formatted victory message
message = config.get_victory_message()  # Returns message with flag

# Update flag content
config.update_flag_content("NEW_CONTENT")  # Updates and saves

# Access any configuration value
value = config.get("victory.flag_prefix", "FLAG{")  # Dot notation access
config.set("victory.flag_content", "NEW_VALUE")  # Set any value
```

### Configuration File Schema

The configuration file follows this JSON schema structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "victory": {
      "type": "object",
      "properties": {
        "flag_content": {"type": "string"},
        "flag_prefix": {"type": "string"},
        "flag_suffix": {"type": "string"},
        "prize_message": {"type": "string"}
      }
    },
    "game": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "version": {"type": "string"}
      }
    }
  }
}
```

## Support and Contributing

### Getting Help
- Check this documentation for common issues
- Review error messages and troubleshooting section
- Test with sample configuration to isolate issues
- Verify JSON syntax and file permissions

### Contributing Improvements
- Submit bug reports with configuration file contents
- Suggest new flag formats or message templates
- Contribute additional troubleshooting scenarios
- Help improve documentation clarity

---

*This documentation covers version 1.0 of the configurable victory flag system. For the latest updates, check the project repository.*