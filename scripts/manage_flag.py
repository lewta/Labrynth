#!/usr/bin/env python3
"""
Flag Management Command-Line Script

This script provides a command-line interface for managing victory flag configuration
in the Labyrinth Adventure Game without requiring manual JSON file editing.
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config.game_config import GameConfig


def show_command(args):
    """Display current flag configuration."""
    try:
        config = GameConfig()
        
        print("Current Flag Configuration:")
        print("=" * 40)
        print(f"Flag Content: {config.get('victory.flag_content')}")
        print(f"Flag Prefix:  {config.get('victory.flag_prefix')}")
        print(f"Flag Suffix:  {config.get('victory.flag_suffix')}")
        print(f"Complete Flag: {config.get_victory_flag()}")
        print()
        print("Victory Message Template:")
        print("-" * 25)
        print(config.get('victory.prize_message'))
        print()
        print("Preview:")
        print("-" * 8)
        print(config.get_victory_message())
        
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        return 1
    
    return 0


def update_command(args):
    """Update flag content with validation."""
    if not args.content:
        print("Error: Flag content cannot be empty", file=sys.stderr)
        return 1
    
    # Basic validation - flag content should not contain spaces or special characters
    # that might cause issues, but we'll be permissive for flexibility
    content = args.content.strip()
    if not content:
        print("Error: Flag content cannot be empty or whitespace only", file=sys.stderr)
        return 1
    
    try:
        config = GameConfig()
        old_content = config.get('victory.flag_content')
        
        # Update the flag content
        config.update_flag_content(content)
        
        print(f"Flag content updated successfully!")
        print(f"Old content: {old_content}")
        print(f"New content: {content}")
        print(f"Complete flag: {config.get_victory_flag()}")
        
    except Exception as e:
        print(f"Error updating flag content: {e}", file=sys.stderr)
        return 1
    
    return 0


def format_command(args):
    """Update flag format (prefix and/or suffix) with validation."""
    if not args.prefix and not args.suffix:
        print("Error: At least one of --prefix or --suffix must be specified", file=sys.stderr)
        return 1
    
    try:
        config = GameConfig()
        
        # Store old values for display
        old_prefix = config.get('victory.flag_prefix')
        old_suffix = config.get('victory.flag_suffix')
        old_flag = config.get_victory_flag()
        
        # Update prefix if provided
        if args.prefix is not None:
            config.set('victory.flag_prefix', args.prefix)
        
        # Update suffix if provided
        if args.suffix is not None:
            config.set('victory.flag_suffix', args.suffix)
        
        # Save configuration
        config.save_config()
        
        print("Flag format updated successfully!")
        if args.prefix is not None:
            print(f"Old prefix: '{old_prefix}' -> New prefix: '{args.prefix}'")
        if args.suffix is not None:
            print(f"Old suffix: '{old_suffix}' -> New suffix: '{args.suffix}'")
        print(f"Old flag: {old_flag}")
        print(f"New flag: {config.get_victory_flag()}")
        
    except Exception as e:
        print(f"Error updating flag format: {e}", file=sys.stderr)
        return 1
    
    return 0


def message_command(args):
    """Update victory message template with validation."""
    if not args.template:
        print("Error: Message template cannot be empty", file=sys.stderr)
        return 1
    
    template = args.template.strip()
    if not template:
        print("Error: Message template cannot be empty or whitespace only", file=sys.stderr)
        return 1
    
    # Validate that template contains {flag} placeholder
    if "{flag}" not in template:
        print("Error: Message template must contain {flag} placeholder", file=sys.stderr)
        return 1
    
    # Test template formatting to ensure it's valid
    try:
        test_flag = "FLAG{TEST}"
        template.format(flag=test_flag)
    except Exception as e:
        print(f"Error: Invalid message template format: {e}", file=sys.stderr)
        return 1
    
    try:
        config = GameConfig()
        old_template = config.get('victory.prize_message')
        
        # Update the message template
        config.set('victory.prize_message', template)
        config.save_config()
        
        print("Victory message template updated successfully!")
        print("\nOld template:")
        print("-" * 13)
        print(old_template)
        print("\nNew template:")
        print("-" * 13)
        print(template)
        print("\nPreview with current flag:")
        print("-" * 26)
        print(config.get_victory_message())
        
    except Exception as e:
        print(f"Error updating message template: {e}", file=sys.stderr)
        return 1
    
    return 0


def sample_command(args):
    """Create sample configuration file with comments and examples."""
    config_file = args.output or "game_config.json"
    
    # Check if file already exists and handle overwrite
    if os.path.exists(config_file) and not args.force:
        print(f"Error: Configuration file '{config_file}' already exists.", file=sys.stderr)
        print("Use --force to overwrite or specify a different output file with --output", file=sys.stderr)
        return 1
    
    # Create sample configuration with comments
    sample_config = {
        "_comment": "Labyrinth Adventure Game Configuration",
        "_description": "This file contains configuration settings for the game, including victory flag customization",
        
        "victory": {
            "_comment": "Victory flag and message configuration",
            "flag_content": "LABYRINTH_MASTER_2024",
            "_flag_content_help": "The main content of the victory flag (without prefix/suffix)",
            
            "flag_prefix": "FLAG{",
            "_flag_prefix_help": "Prefix for the victory flag (e.g., 'FLAG{', 'CTF{', 'CHALLENGE{')",
            
            "flag_suffix": "}",
            "_flag_suffix_help": "Suffix for the victory flag (e.g., '}', ']', ')')",
            
            "prize_message": "🏆 YOUR PRIZE: {flag}\n\nYou have proven yourself worthy of the ancient secrets!",
            "_prize_message_help": "Victory message template. Must contain {flag} placeholder where the flag will be inserted"
        },
        
        "game": {
            "_comment": "General game configuration",
            "title": "Labyrinth Adventure Game",
            "version": "1.0"
        },
        
        "display": {
            "_comment": "Display and UI configuration",
            "width": 80,
            "show_map": True
        },
        
        "_examples": {
            "_comment": "Example configurations for different use cases",
            
            "ctf_event": {
                "victory": {
                    "flag_content": "CYBER_CHALLENGE_2024",
                    "flag_prefix": "CTF{",
                    "flag_suffix": "}",
                    "prize_message": "🎯 CONGRATULATIONS! You've captured the flag: {flag}\n\nWell done, cyber warrior!"
                }
            },
            
            "themed_event": {
                "victory": {
                    "flag_content": "ANCIENT_WISDOM_UNLOCKED",
                    "flag_prefix": "TREASURE{",
                    "flag_suffix": "}",
                    "prize_message": "⚡ VICTORY ACHIEVED! ⚡\n\nYour reward: {flag}\n\nThe ancient labyrinth recognizes your skill!"
                }
            },
            
            "simple_format": {
                "victory": {
                    "flag_content": "SUCCESS_2024",
                    "flag_prefix": "",
                    "flag_suffix": "",
                    "prize_message": "🌟 Congratulations! Your completion code is: {flag}"
                }
            }
        }
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        
        print(f"Sample configuration file created: {config_file}")
        print("\nThe file includes:")
        print("• Default configuration values")
        print("• Helpful comments explaining each setting")
        print("• Example configurations for different use cases")
        print("\nTo use this configuration:")
        print(f"1. Edit {config_file} to customize your settings")
        print("2. Remove or ignore the '_comment' and '_examples' sections")
        print("3. Test your configuration with: python scripts/manage_flag.py test")
        
    except Exception as e:
        print(f"Error creating sample configuration file: {e}", file=sys.stderr)
        return 1
    
    return 0


def test_command(args):
    """Preview flag display using current configuration."""
    try:
        config = GameConfig()
        
        print("Configuration Test Results")
        print("=" * 50)
        
        # Show configuration file being used
        config_file = config.get_config_file_path()
        if config_file:
            print(f"Using configuration file: {config_file}")
        else:
            print("Using default configuration (no config file found)")
        
        # Check if in read-only mode
        if config.is_read_only():
            print("⚠️  WARNING: Configuration is in read-only mode")
        
        print()
        
        # Validate configuration
        validation = config.validate_configuration()
        if validation['valid']:
            print("✅ Configuration validation: PASSED")
        else:
            print("❌ Configuration validation: FAILED")
            for issue in validation['issues']:
                print(f"   • {issue}")
        
        print()
        
        # Show current flag components
        print("Flag Components:")
        print("-" * 16)
        print(f"Content: '{config.get('victory.flag_content')}'")
        print(f"Prefix:  '{config.get('victory.flag_prefix')}'")
        print(f"Suffix:  '{config.get('victory.flag_suffix')}'")
        print(f"Complete Flag: {config.get_victory_flag()}")
        
        print()
        
        # Show victory message preview
        print("Victory Message Preview:")
        print("-" * 24)
        print("┌" + "─" * 78 + "┐")
        
        # Split message into lines and display with border
        message_lines = config.get_victory_message().split('\n')
        for line in message_lines:
            # Truncate long lines and pad short ones
            display_line = line[:76]
            padded_line = display_line.ljust(76)
            print(f"│ {padded_line} │")
        
        print("└" + "─" * 78 + "┘")
        
        print()
        
        # Show template information
        template = config.get('victory.prize_message')
        print("Message Template:")
        print("-" * 17)
        print(f"Template: {repr(template)}")
        print(f"Contains {{flag}} placeholder: {'✅' if '{flag}' in template else '❌'}")
        
        # Test template formatting
        try:
            test_result = template.format(flag="TEST_FLAG")
            print("Template formatting: ✅ Valid")
        except Exception as e:
            print(f"Template formatting: ❌ Error - {e}")
        
        print()
        
        # Show usage suggestions
        print("Usage Suggestions:")
        print("-" * 18)
        if not validation['valid']:
            print("• Fix configuration issues listed above")
        print("• Use 'show' command to see current settings")
        print("• Use 'update' command to change flag content")
        print("• Use 'format' command to change flag prefix/suffix")
        print("• Use 'message' command to change victory message template")
        
    except Exception as e:
        print(f"Error testing configuration: {e}", file=sys.stderr)
        return 1
    
    return 0


def main():
    """Main entry point for the flag management script."""
    parser = argparse.ArgumentParser(
        description="Manage victory flag configuration for Labyrinth Adventure Game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  show                    Display current flag configuration and preview
  update <content>        Update flag content (the main part without prefix/suffix)
  format                  Update flag format (prefix and/or suffix)
  message <template>      Update victory message template
  sample                  Create sample configuration file with examples
  test                    Test and preview current configuration

Examples:
  %(prog)s show                                    # Display current configuration
  %(prog)s update "CYBER_CHALLENGE_2024"          # Update flag content
  %(prog)s format --prefix "CTF{" --suffix "}"    # Update flag format
  %(prog)s message "🎉 Congratulations! Your flag: {flag}"  # Update victory message
  %(prog)s sample --output my_config.json         # Create sample configuration
  %(prog)s test                                    # Test current configuration

Configuration Files:
  The script searches for configuration files in this order:
  1. game_config.json (project root)
  2. config/game_config.json (config directory)  
  3. ~/.labrynth_config.json (user home)

Flag Format:
  Complete flag = prefix + content + suffix
  Example: "FLAG{" + "LABYRINTH_MASTER_2024" + "}" = "FLAG{LABYRINTH_MASTER_2024}"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Show command
    show_parser = subparsers.add_parser(
        'show', 
        help='Display current flag configuration and preview',
        description='Display the current flag configuration, including all components and a preview of how the victory message will appear to players.'
    )
    show_parser.set_defaults(func=show_command)
    
    # Update command
    update_parser = subparsers.add_parser(
        'update', 
        help='Update flag content',
        description='Update the main flag content (the part between prefix and suffix). This is typically the unique identifier for your event or challenge.'
    )
    update_parser.add_argument('content', help='New flag content (e.g., "CYBER_CHALLENGE_2024", "ANCIENT_WISDOM")')
    update_parser.set_defaults(func=update_command)
    
    # Format command
    format_parser = subparsers.add_parser(
        'format', 
        help='Update flag format (prefix and/or suffix)',
        description='Update the flag prefix and/or suffix to change the overall flag format. Useful for adapting to different competition formats.'
    )
    format_parser.add_argument('--prefix', help='New flag prefix (e.g., "CTF{", "CHALLENGE{", "FLAG{")')
    format_parser.add_argument('--suffix', help='New flag suffix (e.g., "}", "]", ")")')
    format_parser.set_defaults(func=format_command)
    
    # Message command
    message_parser = subparsers.add_parser(
        'message', 
        help='Update victory message template',
        description='Update the victory message template that players see when they complete the game. The template must contain {flag} placeholder.'
    )
    message_parser.add_argument('template', help='New victory message template (must contain {flag} placeholder)')
    message_parser.set_defaults(func=message_command)
    
    # Sample command
    sample_parser = subparsers.add_parser(
        'sample', 
        help='Create sample configuration file with examples',
        description='Create a sample configuration file with default values, helpful comments, and examples for different use cases.'
    )
    sample_parser.add_argument('--output', '-o', default='game_config.json', 
                              help='Output file path (default: game_config.json)')
    sample_parser.add_argument('--force', '-f', action='store_true',
                              help='Overwrite existing file if it exists')
    sample_parser.set_defaults(func=sample_command)
    
    # Test command
    test_parser = subparsers.add_parser(
        'test', 
        help='Test and preview current configuration',
        description='Test the current configuration for validity and show a preview of how the victory flag and message will appear to players.'
    )
    test_parser.set_defaults(func=test_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute the command
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())