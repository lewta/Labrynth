"""Challenge system package."""

from .base import Challenge
from .combat import CombatChallenge
from .factory import ChallengeFactory
from .memory import MemoryChallenge
from .puzzle import PuzzleChallenge
from .riddle import RiddleChallenge
from .skill import SkillChallenge

# Register challenge types with the factory
ChallengeFactory.register_challenge_type('riddle', RiddleChallenge)
ChallengeFactory.register_challenge_type('puzzle', PuzzleChallenge)
ChallengeFactory.register_challenge_type('combat', CombatChallenge)
ChallengeFactory.register_challenge_type('skill', SkillChallenge)
ChallengeFactory.register_challenge_type('memory', MemoryChallenge)

__all__ = ['Challenge', 'ChallengeFactory', 'RiddleChallenge', 'PuzzleChallenge', 'CombatChallenge', 'SkillChallenge', 'MemoryChallenge']
