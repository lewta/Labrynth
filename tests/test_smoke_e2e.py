"""End-to-end smoke test: walk from chamber 1 to chamber 13 and win.

This test exercises the full game engine without mocking the core logic.
It is the authoritative check that the game is actually playable.
"""

import pytest
from unittest.mock import Mock

from src.game.engine import GameEngine
from src.game.command_parser import CommandType, ParsedCommand
from src.game.ui_controller import UIController


def _move(engine: GameEngine, direction: str) -> None:
    cmd = ParsedCommand(
        command_type=CommandType.MOVEMENT,
        action="go",
        parameters=[direction],
        raw_input=direction,
        is_valid=True,
    )
    engine.process_command(cmd)


def _answer(engine: GameEngine, text: str) -> None:
    cmd = ParsedCommand(
        command_type=CommandType.CHALLENGE,
        action="answer",
        parameters=[text],
        raw_input=f"answer {text}",
        is_valid=True,
    )
    engine.process_command(cmd)


def _solve_memory(engine: GameEngine, chamber_id: int) -> None:
    """Solve a memory challenge by reading the sequence directly and answering."""
    chamber = engine.world_manager.get_chamber(chamber_id)
    assert chamber is not None
    challenge = chamber.challenge
    assert challenge is not None

    # Phase 1: 'ready' shows the sequence and immediately enters input phase
    _answer(engine, "ready")
    assert challenge.phase == "input", f"Expected 'input', got '{challenge.phase}'"

    # Phase 2: submit the correct answer from the challenge's own sequence data
    if challenge.memory_type == "pattern":
        # Format: "row,col,symbol; row,col,symbol; ..."
        answer = "; ".join(
            f"{r + 1},{c + 1},{s}" for r, c, s in challenge.current_sequence
        )
    else:
        # sequence / color / number — space-separated items
        answer = " ".join(str(item) for item in challenge.current_sequence)

    _answer(engine, answer)
    assert chamber.completed, "Chamber 13 challenge was not completed after correct answer"


@pytest.mark.integration
class TestFullGameWalkthrough:
    """Smoke test: start → navigate → win."""

    def setup_method(self):
        self.engine = GameEngine()
        # Silence all UI output — we're testing logic, not display
        self.engine.ui_controller = Mock(spec=UIController)

    def test_navigate_to_exit_chamber(self):
        """Shortest path from chamber 1 to chamber 13."""
        for direction in ["north", "north", "east", "south", "west", "south"]:
            _move(self.engine, direction)

        assert self.engine.world_manager.current_chamber_id == 13

    def test_win_by_completing_exit_chamber(self):
        """Navigate to chamber 13, solve its challenge, assert win condition."""
        # Navigate: 1 → 2 → 3 → 6 → 9 → 12 → 13
        for direction in ["north", "north", "east", "south", "west", "south"]:
            _move(self.engine, direction)

        assert self.engine.world_manager.current_chamber_id == 13
        assert not self.engine.check_win_condition(), "Should not have won yet"

        _solve_memory(self.engine, 13)

        assert self.engine.check_win_condition(), "Win condition not triggered after completing exit chamber"

    def test_player_survives_to_exit(self):
        """Player should reach chamber 13 with health > 0 without fighting anything."""
        for direction in ["north", "north", "east", "south", "west", "south"]:
            _move(self.engine, direction)

        assert self.engine.player_manager.is_alive()

    def test_victory_display_called_on_win(self):
        """game_loop should call display_game_over(True, ...) when win condition met."""
        # Navigate to exit
        for direction in ["north", "north", "east", "south", "west", "south"]:
            _move(self.engine, direction)

        _solve_memory(self.engine, 13)

        # Trigger the victory handler directly
        self.engine.start_time = 1  # avoid zero division
        self.engine._handle_victory()

        self.engine.ui_controller.display_game_over.assert_called_once()
        call_args = self.engine.ui_controller.display_game_over.call_args
        assert call_args[0][0] is True, "display_game_over should be called with won=True"
