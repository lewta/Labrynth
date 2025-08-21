"""Skill challenge implementation."""

import random
from typing import Optional, Dict, Any, List
from src.challenges.base import Challenge
from src.utils.data_models import Item, ChallengeResult, PlayerStats


class SkillChallenge(Challenge):
    """A skill-based challenge using player stats and random elements."""
    
    # Skill types and their associated stats
    SKILL_TYPES = {
        'strength': {
            'stat': 'strength',
            'name': 'Strength Challenge',
            'description': 'A test of physical power and endurance',
            'actions': ['lift', 'push', 'break', 'climb', 'force']
        },
        'intelligence': {
            'stat': 'intelligence',
            'name': 'Intelligence Challenge',
            'description': 'A test of mental acuity and problem-solving',
            'actions': ['analyze', 'calculate', 'deduce', 'reason', 'solve']
        },
        'dexterity': {
            'stat': 'dexterity',
            'name': 'Dexterity Challenge',
            'description': 'A test of agility and precise movement',
            'actions': ['dodge', 'balance', 'sneak', 'pick', 'jump']
        },
        'luck': {
            'stat': 'luck',
            'name': 'Luck Challenge',
            'description': 'A test of fortune and chance',
            'actions': ['gamble', 'risk', 'chance', 'try', 'hope']
        }
    }
    
    def __init__(self, difficulty: int = 5, skill_type: str = None, 
                 reward_item: Item = None, **kwargs):
        """Initialize a skill challenge.
        
        Args:
            difficulty: Difficulty level (1-10)
            skill_type: Type of skill to test ('strength', 'intelligence', 'dexterity', 'luck')
            reward_item: Item to give as reward for success
            **kwargs: Additional arguments
        """
        # Choose random skill type if not specified
        if skill_type is None:
            skill_type = random.choice(list(self.SKILL_TYPES.keys()))
        
        if skill_type not in self.SKILL_TYPES:
            raise ValueError(f"Invalid skill type: {skill_type}. Must be one of {list(self.SKILL_TYPES.keys())}")
        
        self.skill_type = skill_type
        skill_info = self.SKILL_TYPES[skill_type]
        
        name = kwargs.get('name', skill_info['name'])
        description = kwargs.get('description', skill_info['description'])
        
        super().__init__(name, description, difficulty)
        
        # Challenge state
        self.attempts = 0
        self.max_attempts = 3
        self.success_threshold = self._calculate_success_threshold()
        self.challenge_scenario = self._generate_scenario()
        
        # Reward
        self.reward_item = reward_item or self._get_default_reward()
    
    def _calculate_success_threshold(self) -> int:
        """Calculate the success threshold based on difficulty.
        
        Returns:
            The minimum roll needed to succeed
        """
        # Base threshold increases with difficulty
        # Difficulty 1: need 30+, Difficulty 10: need 75+
        base_threshold = 25 + (self.difficulty * 5)
        return min(base_threshold, 80)  # Cap at 80 to always leave some chance
    
    def _generate_scenario(self) -> Dict[str, str]:
        """Generate a scenario description for the skill challenge.
        
        Returns:
            Dictionary with scenario details
        """
        scenarios = {
            'strength': [
                "A massive boulder blocks your path. You need to move it aside.",
                "Heavy iron bars block a doorway. You must bend them to pass.",
                "A deep pit requires you to climb up using only your grip strength.",
                "Ancient chains bind a treasure chest. You need to break them.",
                "A stone door is stuck shut and requires great force to open."
            ],
            'intelligence': [
                "Ancient symbols cover the wall. You must decipher their meaning.",
                "A complex mechanical puzzle blocks your way forward.",
                "Mysterious runes glow with power. You need to understand their pattern.",
                "A riddle is carved in stone, but it's written in an ancient language.",
                "Multiple levers control a mechanism. You must determine the correct sequence."
            ],
            'dexterity': [
                "Pressure plates cover the floor. You must navigate without triggering them.",
                "A narrow ledge spans a dangerous chasm. You need perfect balance.",
                "Spinning blades block the passage. You must time your movement precisely.",
                "A complex lock requires delicate manipulation to open.",
                "Swinging pendulums guard the exit. You need to slip through at the right moment."
            ],
            'luck': [
                "Three identical doors stand before you. Only one leads forward safely.",
                "A magical wheel spins with various symbols. You must choose when to stop it.",
                "Ancient dice lie on a pedestal. The gods will judge your fortune.",
                "A shimmering portal flickers unstably. You must time your entry perfectly.",
                "Five treasure chests sit before you, but only one contains what you need."
            ]
        }
        
        scenario_text = random.choice(scenarios[self.skill_type])
        skill_info = self.SKILL_TYPES[self.skill_type]
        action_word = random.choice(skill_info['actions'])
        
        return {
            'scenario': scenario_text,
            'action': action_word,
            'stat': skill_info['stat']
        }
    
    def _get_default_reward(self) -> Item:
        """Get a default reward item based on skill type and difficulty."""
        reward_types = {
            'strength': ["Power Gauntlets", "Strength Potion", "Mighty Belt", "Iron Ring"],
            'intelligence': ["Wisdom Scroll", "Knowledge Crystal", "Scholar's Tome", "Mind Gem"],
            'dexterity': ["Agility Boots", "Swift Cloak", "Nimble Ring", "Grace Amulet"],
            'luck': ["Fortune Coin", "Lucky Charm", "Fate Stone", "Blessed Token"]
        }
        
        rewards = reward_types[self.skill_type]
        reward_name = rewards[min(self.difficulty // 3, len(rewards) - 1)]
        
        return Item(
            name=reward_name,
            description=f"A {reward_name.lower()} that enhances your {self.skill_type}",
            item_type="enhancement",
            value=self.difficulty * 12
        )
    
    def present_challenge(self) -> str:
        """Present the skill challenge to the player."""
        presentation = f"\n=== {self.name} ===\n"
        presentation += f"Difficulty: {self.difficulty}/10\n"
        presentation += f"Primary Stat: {self.skill_type.title()}\n\n"
        
        presentation += f"{self.challenge_scenario['scenario']}\n\n"
        
        if self.attempts > 0:
            remaining = self.max_attempts - self.attempts
            presentation += f"Attempts remaining: {remaining}\n\n"
        
        presentation += f"This challenge tests your {self.skill_type}. "
        presentation += f"Type '{self.challenge_scenario['action']}' to attempt the challenge, "
        presentation += "or 'examine' to study the situation more carefully.\n\n"
        presentation += "What do you do? "
        
        return presentation
    
    def process_response(self, response: str, player_stats: PlayerStats = None) -> ChallengeResult:
        """Process the player's response to the skill challenge.
        
        Args:
            response: The player's action
            player_stats: Player's current stats (optional)
            
        Returns:
            ChallengeResult indicating success/failure and any rewards
        """
        if player_stats is None:
            player_stats = PlayerStats()  # Default stats
        
        action = response.lower().strip()
        
        if action == 'examine':
            return self._examine_challenge(player_stats)
        elif action == self.challenge_scenario['action'] or action in ['attempt', 'try', 'do']:
            return self._attempt_challenge(player_stats)
        else:
            return ChallengeResult(
                success=False,
                message=f"Invalid action! Use '{self.challenge_scenario['action']}' to attempt the challenge or 'examine' to study it.",
                is_intermediate=True
            )
    
    def _examine_challenge(self, player_stats: PlayerStats) -> ChallengeResult:
        """Allow player to examine the challenge for hints.
        
        Args:
            player_stats: Player's stats
            
        Returns:
            ChallengeResult with examination information
        """
        stat_value = player_stats.get_stat(self.skill_type)
        
        # Provide hints based on player's relevant stat
        if stat_value >= 15:
            hint = "You feel very confident about this challenge. Your skills are well-suited for this task."
        elif stat_value >= 12:
            hint = "You think you have a good chance of succeeding with careful effort."
        elif stat_value >= 8:
            hint = "This will be challenging, but not impossible. You'll need some luck."
        else:
            hint = "This looks very difficult for someone with your current abilities."
        
        # Add difficulty-specific hints
        if self.difficulty <= 3:
            difficulty_hint = "The challenge appears straightforward."
        elif self.difficulty <= 6:
            difficulty_hint = "The challenge looks moderately complex."
        else:
            difficulty_hint = "The challenge appears extremely demanding."
        
        message = f"You carefully examine the situation. {hint} {difficulty_hint}"
        
        return ChallengeResult(
            success=False,
            message=message,
            is_intermediate=True
        )
    
    def _attempt_challenge(self, player_stats: PlayerStats) -> ChallengeResult:
        """Attempt the skill challenge.
        
        Args:
            player_stats: Player's stats
            
        Returns:
            ChallengeResult with attempt outcome
        """
        self.attempts += 1
        
        # Get relevant stat value
        stat_value = player_stats.get_stat(self.skill_type)
        
        # Calculate success probability
        success_chance = self._calculate_success_chance(stat_value)
        
        # Roll for success (1-100)
        roll = random.randint(1, 100)
        
        # Determine outcome
        if roll <= success_chance:
            # Success!
            self.mark_completed()
            success_message = self._get_success_message(roll, success_chance)
            return ChallengeResult(
                success=True,
                message=success_message,
                reward=self.reward_item
            )
        else:
            # Failure
            remaining_attempts = self.max_attempts - self.attempts
            
            if remaining_attempts > 0:
                failure_message = self._get_failure_message(roll, success_chance, remaining_attempts)
                return ChallengeResult(
                    success=False,
                    message=failure_message
                )
            else:
                # No more attempts
                final_failure_message = self._get_final_failure_message()
                return ChallengeResult(
                    success=False,
                    message=final_failure_message,
                    damage=self._calculate_failure_damage()
                )
    
    def _calculate_success_chance(self, stat_value: int) -> int:
        """Calculate success chance based on stat value and difficulty.
        
        Args:
            stat_value: Player's relevant stat value
            
        Returns:
            Success chance as percentage (0-100)
        """
        # Base chance starts at 50%
        base_chance = 50
        
        # Stat modifier: each point above/below 10 gives +/-3%
        stat_modifier = (stat_value - 10) * 3
        
        # Difficulty modifier: each difficulty point above 5 reduces chance by 4%
        difficulty_modifier = -(self.difficulty - 5) * 4
        
        # Calculate final chance
        final_chance = base_chance + stat_modifier + difficulty_modifier
        
        # Clamp between 5% and 95%
        return max(5, min(95, final_chance))
    
    def _calculate_failure_damage(self) -> int:
        """Calculate damage taken on final failure.
        
        Returns:
            Damage amount
        """
        # Base damage increases with difficulty
        base_damage = 3 + self.difficulty
        
        # Add some randomness
        variance = random.randint(-2, 3)
        
        return max(1, base_damage + variance)
    
    def _get_success_message(self, roll: int, success_chance: int) -> str:
        """Get success message based on roll quality.
        
        Args:
            roll: The dice roll result
            success_chance: The success chance percentage
            
        Returns:
            Success message
        """
        if roll <= success_chance // 3:
            quality = "masterfully"
        elif roll <= success_chance // 2:
            quality = "skillfully"
        else:
            quality = "successfully"
        
        messages = {
            'strength': f"You {quality} overcome the physical challenge through sheer power!",
            'intelligence': f"You {quality} solve the mental puzzle with clever thinking!",
            'dexterity': f"You {quality} navigate the challenge with precise movements!",
            'luck': f"Fortune smiles upon you as you {quality} make the right choice!"
        }
        
        return messages[self.skill_type]
    
    def _get_failure_message(self, roll: int, success_chance: int, remaining: int) -> str:
        """Get failure message for non-final attempts.
        
        Args:
            roll: The dice roll result
            success_chance: The success chance percentage
            remaining: Remaining attempts
            
        Returns:
            Failure message
        """
        if roll > success_chance + 30:
            quality = "badly"
        elif roll > success_chance + 15:
            quality = "poorly"
        else:
            quality = "narrowly"
        
        messages = {
            'strength': f"You {quality} fail to overcome the physical challenge.",
            'intelligence': f"You {quality} fail to solve the mental puzzle.",
            'dexterity': f"You {quality} fail to navigate the challenge precisely.",
            'luck': f"Fortune does not favor you this time."
        }
        
        base_message = messages[self.skill_type]
        return f"{base_message} You have {remaining} attempt(s) remaining."
    
    def _get_final_failure_message(self) -> str:
        """Get message for final failure.
        
        Returns:
            Final failure message
        """
        messages = {
            'strength': "Despite your best efforts, you lack the physical power needed. You strain yourself in the attempt.",
            'intelligence': "The mental challenge proves too complex for you to solve. The effort leaves you mentally drained.",
            'dexterity': "Your movements aren't precise enough to overcome the challenge. You suffer minor injuries from your clumsy attempts.",
            'luck': "Fortune has completely abandoned you. Your poor choices lead to unfortunate consequences."
        }
        
        return messages[self.skill_type]
    
    def get_reward(self) -> Optional[Item]:
        """Get the reward for completing this skill challenge.
        
        Returns:
            The reward item if challenge is completed, None otherwise
        """
        return self.reward_item if self.completed else None
    
    def reset(self) -> None:
        """Reset the skill challenge for a new attempt."""
        self.attempts = 0
        self.completed = False
        # Generate new scenario for variety
        self.challenge_scenario = self._generate_scenario()
    
    def get_challenge_info(self) -> Dict[str, Any]:
        """Get detailed information about the challenge.
        
        Returns:
            Dictionary with challenge details
        """
        return {
            "skill_type": self.skill_type,
            "difficulty": self.difficulty,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "success_threshold": self.success_threshold,
            "scenario": self.challenge_scenario,
            "completed": self.completed
        }
    
    def get_success_chance_for_stats(self, player_stats: PlayerStats) -> int:
        """Get success chance for given player stats (for UI/planning).
        
        Args:
            player_stats: Player's stats
            
        Returns:
            Success chance percentage
        """
        stat_value = player_stats.get_stat(self.skill_type)
        return self._calculate_success_chance(stat_value)