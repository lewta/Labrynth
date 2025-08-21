"""Combat challenge implementation."""

import random
from typing import Optional, Dict, Any
from src.challenges.base import Challenge
from src.utils.data_models import Item, ChallengeResult, PlayerStats
from src.utils.challenge_content import get_content_loader


class Enemy:
    """Represents an enemy in combat."""
    
    def __init__(self, name: str, health: int, attack: int, defense: int):
        """Initialize an enemy.
        
        Args:
            name: Enemy name
            health: Enemy health points
            attack: Enemy attack power
            defense: Enemy defense rating
        """
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defense = defense
    
    def is_alive(self) -> bool:
        """Check if enemy is still alive."""
        return self.health > 0
    
    def take_damage(self, damage: int) -> int:
        """Apply damage to enemy.
        
        Args:
            damage: Damage amount
            
        Returns:
            Actual damage dealt after defense
        """
        actual_damage = max(1, damage - self.defense)  # Minimum 1 damage
        self.health = max(0, self.health - actual_damage)
        return actual_damage
    
    def attack_player(self) -> int:
        """Calculate enemy attack damage with some randomness.
        
        Returns:
            Damage to deal to player
        """
        base_damage = self.attack
        # Add some randomness (±25%)
        variance = int(base_damage * 0.25)
        damage = random.randint(base_damage - variance, base_damage + variance)
        return max(1, damage)


class CombatChallenge(Challenge):
    """A turn-based combat challenge with simple attack/defend mechanics."""
    
    def __init__(self, difficulty: int = 5, enemy_name: str = None, 
                 reward_item: Item = None, **kwargs):
        """Initialize a combat challenge.
        
        Args:
            difficulty: Difficulty level (1-10)
            enemy_name: Name of the enemy to fight
            reward_item: Item to give as reward for winning
            **kwargs: Additional arguments
        """
        name = kwargs.get('name', 'Combat Challenge')
        description = kwargs.get('description', 'A dangerous enemy blocks your path')
        
        super().__init__(name, description, difficulty)
        
        # Create enemy based on difficulty (with potential randomization)
        self.enemy = self._create_enemy(enemy_name, difficulty)
        
        # Try to get randomized combat scenario
        self.combat_scenario = self._get_combat_scenario()
        
        # Combat state
        self.combat_active = False
        self.player_health = 100  # Will be updated when combat starts
        self.turn_count = 0
        self.combat_log = []
        
        # Reward
        self.reward_item = reward_item or self._get_default_reward()
    
    def _create_enemy(self, enemy_name: str = None, difficulty: int = 5) -> Enemy:
        """Create an enemy based on difficulty level.
        
        Args:
            enemy_name: Optional enemy name
            difficulty: Difficulty level
            
        Returns:
            Enemy instance
        """
        # Try to get randomized enemy from content loader
        try:
            if enemy_name is None:
                content_loader = get_content_loader()
                enemy_data = content_loader.get_enemy(difficulty)
                return Enemy(
                    name=enemy_data.get('name', 'Unknown Enemy'),
                    health=enemy_data.get('health', 50),
                    attack=enemy_data.get('attack', 10),
                    defense=enemy_data.get('defense', 2)
                )
        except Exception:
            # Fall back to default templates
            pass
        
        # Default enemy templates based on difficulty
        enemy_templates = {
            1: {"name": "Weak Goblin", "health": 20, "attack": 5, "defense": 1},
            2: {"name": "Cave Rat", "health": 25, "attack": 6, "defense": 1},
            3: {"name": "Skeleton Warrior", "health": 35, "attack": 8, "defense": 2},
            4: {"name": "Orc Raider", "health": 45, "attack": 10, "defense": 3},
            5: {"name": "Shadow Beast", "health": 55, "attack": 12, "defense": 4},
            6: {"name": "Stone Golem", "health": 70, "attack": 14, "defense": 6},
            7: {"name": "Fire Elemental", "health": 65, "attack": 18, "defense": 3},
            8: {"name": "Dark Knight", "health": 85, "attack": 16, "defense": 8},
            9: {"name": "Ancient Dragon", "health": 120, "attack": 22, "defense": 10},
            10: {"name": "Demon Lord", "health": 150, "attack": 25, "defense": 12}
        }
        
        template = enemy_templates.get(difficulty, enemy_templates[5])
        
        # Use custom name if provided
        if enemy_name:
            template["name"] = enemy_name
        
        return Enemy(**template)
    
    def _get_combat_scenario(self) -> Dict[str, Any]:
        """Get a combat scenario (randomized if available).
        
        Returns:
            Dictionary containing combat scenario data
        """
        try:
            content_loader = get_content_loader()
            return content_loader.get_combat_scenario()
        except Exception:
            # Default scenario
            return {
                'type': 'guard',
                'description': '{enemy_name} blocks your path forward.',
                'initiative_bonus': 0
            }
    
    def _get_default_reward(self) -> Item:
        """Get a default reward item based on difficulty."""
        reward_names = [
            "Rusty Sword", "Iron Dagger", "Steel Blade", "Magic Sword",
            "Enchanted Axe", "Legendary Spear", "Dragon Slayer", "Divine Weapon"
        ]
        
        reward_name = reward_names[min(self.difficulty - 1, len(reward_names) - 1)]
        
        return Item(
            name=reward_name,
            description=f"A {reward_name.lower()} taken from a defeated enemy",
            item_type="weapon",
            value=self.difficulty * 15
        )
    
    def present_challenge(self) -> str:
        """Present the combat challenge to the player."""
        if not self.combat_active:
            # Initial presentation
            presentation = f"\n=== {self.name} ===\n"
            presentation += f"Difficulty: {self.difficulty}/10\n\n"
            # Use scenario description if available
            scenario_desc = self.combat_scenario.get('description', '{enemy_name} blocks your path forward.')
            scenario_text = scenario_desc.format(enemy_name=self.enemy.name)
            presentation += f"{scenario_text}\n"
            presentation += f"Enemy Health: {self.enemy.health}/{self.enemy.max_health}\n\n"
            presentation += "Combat Commands:\n"
            presentation += "- 'attack' or 'a': Attack the enemy\n"
            presentation += "- 'defend' or 'd': Defend to reduce incoming damage\n"
            presentation += "- 'flee' or 'f': Attempt to flee from combat\n\n"
            presentation += "What do you do? "
            return presentation
        else:
            # Combat in progress
            presentation = f"\n--- Turn {self.turn_count} ---\n"
            presentation += f"Your Health: {self.player_health}\n"
            presentation += f"{self.enemy.name} Health: {self.enemy.health}/{self.enemy.max_health}\n\n"
            
            # Show recent combat log
            if self.combat_log:
                presentation += "Recent actions:\n"
                for log_entry in self.combat_log[-3:]:  # Show last 3 entries
                    presentation += f"- {log_entry}\n"
                presentation += "\n"
            
            presentation += "What do you do? (attack/defend/flee) "
            return presentation
    
    def process_response(self, response: str, player_stats: PlayerStats = None) -> ChallengeResult:
        """Process the player's combat action.
        
        Args:
            response: The player's action
            player_stats: Player's current stats (optional)
            
        Returns:
            ChallengeResult indicating the outcome
        """
        if player_stats is None:
            player_stats = PlayerStats()  # Default stats
        
        if not self.combat_active:
            self.combat_active = True
            self.player_health = 100  # Start with full health for challenge
        
        self.turn_count += 1
        action = response.lower().strip()
        
        # Process player action
        if action in ['attack', 'a']:
            return self._process_attack(player_stats)
        elif action in ['defend', 'd']:
            return self._process_defend(player_stats)
        elif action in ['flee', 'f']:
            return self._process_flee(player_stats)
        else:
            return ChallengeResult(
                success=False,
                message="Invalid action! Use 'attack', 'defend', or 'flee'.",
                is_intermediate=True
            )
    
    def _process_attack(self, player_stats: PlayerStats) -> ChallengeResult:
        """Process player attack action.
        
        Args:
            player_stats: Player's stats
            
        Returns:
            ChallengeResult with combat outcome
        """
        # Calculate player damage based on strength
        base_damage = 8 + (player_stats.strength - 10)  # Base 8, +/- based on strength
        
        # Add some randomness and luck factor
        luck_bonus = (player_stats.luck - 10) // 2
        variance = random.randint(-2, 3) + luck_bonus
        player_damage = max(1, base_damage + variance)
        
        # Apply damage to enemy
        actual_damage = self.enemy.take_damage(player_damage)
        self.combat_log.append(f"You attack for {actual_damage} damage!")
        
        # Check if enemy is defeated
        if not self.enemy.is_alive():
            self.mark_completed()
            return ChallengeResult(
                success=True,
                message=f"Victory! You defeated the {self.enemy.name}!",
                reward=self.reward_item
            )
        
        # Enemy attacks back
        enemy_damage = self.enemy.attack_player()
        self.player_health -= enemy_damage
        self.combat_log.append(f"{self.enemy.name} attacks you for {enemy_damage} damage!")
        
        # Check if player is defeated
        if self.player_health <= 0:
            return ChallengeResult(
                success=False,
                message=f"Defeat! The {self.enemy.name} has bested you in combat.",
                damage=25  # Penalty for losing combat
            )
        
        # Combat continues
        return ChallengeResult(
            success=False,
            message="Combat continues...",
            is_intermediate=True
        )
    
    def _process_defend(self, player_stats: PlayerStats) -> ChallengeResult:
        """Process player defend action.
        
        Args:
            player_stats: Player's stats
            
        Returns:
            ChallengeResult with combat outcome
        """
        self.combat_log.append("You raise your guard defensively!")
        
        # Enemy attacks with reduced damage
        enemy_damage = self.enemy.attack_player()
        
        # Calculate defense reduction based on dexterity
        defense_bonus = (player_stats.dexterity - 10) // 2
        damage_reduction = 3 + max(0, defense_bonus)  # Base 3 reduction + dex bonus
        
        reduced_damage = max(1, enemy_damage - damage_reduction)
        self.player_health -= reduced_damage
        
        self.combat_log.append(f"{self.enemy.name} attacks but you block some damage! You take {reduced_damage} damage.")
        
        # Check if player is defeated
        if self.player_health <= 0:
            return ChallengeResult(
                success=False,
                message=f"Defeat! The {self.enemy.name} has overwhelmed your defenses.",
                damage=25
            )
        
        # Combat continues
        return ChallengeResult(
            success=False,
            message="You successfully defended against the attack!",
            is_intermediate=True
        )
    
    def _process_flee(self, player_stats: PlayerStats) -> ChallengeResult:
        """Process player flee action.
        
        Args:
            player_stats: Player's stats
            
        Returns:
            ChallengeResult with flee outcome
        """
        # Calculate flee chance based on dexterity and luck
        base_flee_chance = 60  # 60% base chance
        dex_bonus = (player_stats.dexterity - 10) * 2
        luck_bonus = (player_stats.luck - 10) * 2
        
        flee_chance = base_flee_chance + dex_bonus + luck_bonus
        flee_chance = max(20, min(90, flee_chance))  # Clamp between 20% and 90%
        
        if random.randint(1, 100) <= flee_chance:
            # Successful flee
            return ChallengeResult(
                success=False,
                message=f"You successfully flee from the {self.enemy.name}! You can try again later.",
                damage=5  # Small penalty for fleeing
            )
        else:
            # Failed flee - enemy gets free attack
            enemy_damage = self.enemy.attack_player()
            self.player_health -= enemy_damage
            self.combat_log.append(f"Failed to flee! {self.enemy.name} attacks you for {enemy_damage} damage!")
            
            if self.player_health <= 0:
                return ChallengeResult(
                    success=False,
                    message=f"You failed to escape and the {self.enemy.name} finished you off!",
                    damage=25
                )
            
            return ChallengeResult(
                success=False,
                message="You failed to flee and took damage! Combat continues.",
                is_intermediate=True
            )
    
    def get_reward(self) -> Optional[Item]:
        """Get the reward for completing this combat challenge.
        
        Returns:
            The reward item if combat is won, None otherwise
        """
        return self.reward_item if self.completed else None
    
    def reset(self) -> None:
        """Reset the combat challenge for a new attempt."""
        self.combat_active = False
        self.player_health = 100
        self.turn_count = 0
        self.combat_log.clear()
        self.completed = False
        
        # Reset enemy health
        self.enemy.health = self.enemy.max_health
    
    def get_combat_state(self) -> Dict[str, Any]:
        """Get current combat state information.
        
        Returns:
            Dictionary with combat state details
        """
        return {
            "combat_active": self.combat_active,
            "player_health": self.player_health,
            "enemy_name": self.enemy.name,
            "enemy_health": self.enemy.health,
            "enemy_max_health": self.enemy.max_health,
            "turn_count": self.turn_count,
            "completed": self.completed
        }