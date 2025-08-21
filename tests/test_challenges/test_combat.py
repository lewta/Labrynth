"""Tests for CombatChallenge class."""

import pytest
from unittest.mock import patch
from src.challenges.combat import CombatChallenge, Enemy
from src.utils.data_models import Item, ChallengeResult, PlayerStats


class TestEnemy:
    """Test cases for Enemy class."""
    
    def test_enemy_initialization(self):
        """Test enemy is initialized correctly."""
        enemy = Enemy("Test Goblin", 30, 8, 2)
        
        assert enemy.name == "Test Goblin"
        assert enemy.health == 30
        assert enemy.max_health == 30
        assert enemy.attack == 8
        assert enemy.defense == 2
        assert enemy.is_alive() is True
    
    def test_enemy_take_damage(self):
        """Test enemy takes damage correctly."""
        enemy = Enemy("Test Enemy", 30, 8, 2)
        
        # Test normal damage (10 damage - 2 defense = 8 actual damage)
        actual_damage = enemy.take_damage(10)
        assert actual_damage == 8
        assert enemy.health == 22
        
        # Test minimum damage (1 damage - 2 defense = 1 minimum damage)
        actual_damage = enemy.take_damage(1)
        assert actual_damage == 1
        assert enemy.health == 21
    
    def test_enemy_death(self):
        """Test enemy death mechanics."""
        enemy = Enemy("Test Enemy", 10, 5, 1)
        
        # Deal enough damage to kill
        enemy.take_damage(20)
        assert enemy.health == 0
        assert enemy.is_alive() is False
    
    @patch('random.randint')
    def test_enemy_attack_player(self, mock_random):
        """Test enemy attack calculation."""
        enemy = Enemy("Test Enemy", 30, 10, 2)
        
        # Mock random to return maximum variance
        mock_random.return_value = 12  # 10 + 2 (25% of 10 rounded down)
        damage = enemy.attack_player()
        assert damage == 12
        
        # Mock random to return minimum variance
        mock_random.return_value = 8  # 10 - 2
        damage = enemy.attack_player()
        assert damage == 8


class TestCombatChallenge:
    """Test cases for CombatChallenge class."""
    
    def test_combat_challenge_initialization(self):
        """Test combat challenge is initialized correctly."""
        challenge = CombatChallenge(difficulty=5)
        
        assert challenge.name == "Combat Challenge"
        assert challenge.difficulty == 5
        assert challenge.enemy is not None
        assert challenge.enemy.name == "Shadow Beast"  # Default for difficulty 5
        assert challenge.combat_active is False
        assert challenge.turn_count == 0
        assert challenge.reward_item is not None
    
    def test_custom_enemy_name(self):
        """Test combat challenge with custom enemy name."""
        challenge = CombatChallenge(difficulty=3, enemy_name="Custom Monster")
        
        assert challenge.enemy.name == "Custom Monster"
        assert challenge.enemy.health == 35  # Health should match difficulty 3 template
    
    def test_custom_reward(self):
        """Test combat challenge with custom reward."""
        custom_reward = Item("Test Sword", "A test weapon", "weapon", 100)
        challenge = CombatChallenge(difficulty=5, reward_item=custom_reward)
        
        assert challenge.reward_item == custom_reward
    
    def test_present_challenge_initial(self):
        """Test initial challenge presentation."""
        challenge = CombatChallenge(difficulty=3)
        presentation = challenge.present_challenge()
        
        assert "Combat Challenge" in presentation
        assert "Skeleton Warrior" in presentation
        assert "attack" in presentation
        assert "defend" in presentation
        assert "flee" in presentation
    
    def test_present_challenge_during_combat(self):
        """Test challenge presentation during active combat."""
        challenge = CombatChallenge(difficulty=3)
        challenge.combat_active = True
        challenge.turn_count = 2
        challenge.player_health = 80
        challenge.combat_log = ["You attack for 5 damage!", "Enemy attacks for 10 damage!"]
        
        presentation = challenge.present_challenge()
        
        assert "Turn 2" in presentation
        assert "Your Health: 80" in presentation
        assert "You attack for 5 damage!" in presentation
    
    def test_invalid_action(self):
        """Test invalid combat action."""
        challenge = CombatChallenge(difficulty=1)
        result = challenge.process_response("invalid_action")
        
        assert result.success is False
        assert "Invalid action" in result.message
    
    @patch('random.randint')
    def test_successful_attack(self, mock_random):
        """Test successful player attack."""
        challenge = CombatChallenge(difficulty=1)  # Weak enemy with 20 health
        player_stats = PlayerStats(strength=15, luck=12)
        
        # Mock random for consistent damage
        mock_random.return_value = 2  # Damage variance
        
        result = challenge.process_response("attack", player_stats)
        
        assert challenge.combat_active is True
        assert challenge.turn_count == 1
        assert len(challenge.combat_log) >= 1
        assert "attack" in challenge.combat_log[0].lower()
    
    @patch('random.randint')
    def test_player_victory(self, mock_random):
        """Test player victory in combat."""
        challenge = CombatChallenge(difficulty=1)  # Weak enemy
        player_stats = PlayerStats(strength=20, luck=15)
        
        # Mock high damage to ensure victory
        mock_random.return_value = 5
        
        # Attack until victory (should be quick with weak enemy)
        result = None
        for _ in range(10):  # Safety limit
            result = challenge.process_response("attack", player_stats)
            if result.success:
                break
        
        assert result.success is True
        assert "Victory" in result.message
        assert result.reward is not None
        assert challenge.completed is True
    
    @patch('random.randint')
    def test_defend_action(self, mock_random):
        """Test defend action reduces damage."""
        challenge = CombatChallenge(difficulty=3)
        player_stats = PlayerStats(dexterity=15)
        
        # Mock enemy attack damage
        mock_random.return_value = 10
        
        result = challenge.process_response("defend", player_stats)
        
        assert challenge.combat_active is True
        assert "defended" in result.message.lower() or "block" in result.message.lower()
        assert len(challenge.combat_log) >= 1
    
    @patch('random.randint')
    def test_successful_flee(self, mock_random):
        """Test successful flee attempt."""
        challenge = CombatChallenge(difficulty=3)
        player_stats = PlayerStats(dexterity=15, luck=15)
        
        # Mock successful flee (high roll)
        mock_random.return_value = 50  # Should be within flee chance
        
        result = challenge.process_response("flee", player_stats)
        
        assert result.success is False  # Fleeing is not "success"
        assert "flee" in result.message.lower()
        assert result.damage == 5  # Flee penalty
    
    @patch('random.randint')
    def test_failed_flee(self, mock_random):
        """Test failed flee attempt."""
        challenge = CombatChallenge(difficulty=3)
        player_stats = PlayerStats(dexterity=5, luck=5)
        
        # Mock failed flee (low stats, high roll needed)
        mock_random.side_effect = [95, 8]  # First for flee chance, second for enemy damage
        
        result = challenge.process_response("flee", player_stats)
        
        assert result.success is False
        assert "failed to flee" in result.message.lower()
        assert len(challenge.combat_log) >= 1
    
    def test_player_defeat(self):
        """Test player defeat scenario."""
        challenge = CombatChallenge(difficulty=1)
        challenge.combat_active = True
        challenge.player_health = 1  # Very low health
        
        # Attack should result in player taking damage and potentially dying
        result = challenge.process_response("attack")
        
        # Either player dies immediately or after enemy counter-attack
        if not result.success and "Defeat" in result.message:
            assert result.damage == 25  # Death penalty
    
    def test_get_reward_when_completed(self):
        """Test getting reward when challenge is completed."""
        challenge = CombatChallenge(difficulty=5)
        challenge.mark_completed()
        
        reward = challenge.get_reward()
        assert reward is not None
        assert reward.item_type == "weapon"
    
    def test_get_reward_when_not_completed(self):
        """Test getting reward when challenge is not completed."""
        challenge = CombatChallenge(difficulty=5)
        
        reward = challenge.get_reward()
        assert reward is None
    
    def test_reset_challenge(self):
        """Test resetting the combat challenge."""
        challenge = CombatChallenge(difficulty=3)
        
        # Simulate some combat
        challenge.combat_active = True
        challenge.player_health = 50
        challenge.turn_count = 5
        challenge.combat_log = ["Some combat action"]
        challenge.enemy.health = 10
        challenge.mark_completed()
        
        # Reset
        challenge.reset()
        
        assert challenge.combat_active is False
        assert challenge.player_health == 100
        assert challenge.turn_count == 0
        assert len(challenge.combat_log) == 0
        assert challenge.enemy.health == challenge.enemy.max_health
        assert challenge.completed is False
    
    def test_get_combat_state(self):
        """Test getting combat state information."""
        challenge = CombatChallenge(difficulty=4)
        challenge.combat_active = True
        challenge.player_health = 75
        challenge.turn_count = 3
        
        state = challenge.get_combat_state()
        
        assert state["combat_active"] is True
        assert state["player_health"] == 75
        assert state["enemy_name"] == "Orc Raider"
        assert state["turn_count"] == 3
        assert "enemy_health" in state
        assert "enemy_max_health" in state
        assert "completed" in state
    
    def test_difficulty_scaling(self):
        """Test that enemy difficulty scales with challenge difficulty."""
        easy_challenge = CombatChallenge(difficulty=1)
        hard_challenge = CombatChallenge(difficulty=10)
        
        # Hard challenge should have stronger enemy
        assert hard_challenge.enemy.health > easy_challenge.enemy.health
        assert hard_challenge.enemy.attack > easy_challenge.enemy.attack
        assert hard_challenge.enemy.defense >= easy_challenge.enemy.defense
    
    def test_player_stats_affect_combat(self):
        """Test that player stats affect combat outcomes."""
        challenge = CombatChallenge(difficulty=3)
        
        weak_stats = PlayerStats(strength=5, dexterity=5, luck=5)
        strong_stats = PlayerStats(strength=20, dexterity=20, luck=20)
        
        # This test verifies the stats are used in calculations
        # We can't easily test exact outcomes due to randomness, but we can verify
        # the methods accept and use the stats
        result1 = challenge.process_response("attack", weak_stats)
        challenge.reset()
        result2 = challenge.process_response("attack", strong_stats)
        
        # Both should process without error
        assert isinstance(result1, ChallengeResult)
        assert isinstance(result2, ChallengeResult)


class TestCombatChallengeEdgeCases:
    """Test edge cases for CombatChallenge."""
    
    def test_extreme_difficulty_levels(self):
        """Test combat challenge with extreme difficulty levels."""
        # Very easy
        easy_challenge = CombatChallenge(difficulty=1)
        assert easy_challenge.enemy.health <= 25
        
        # Very hard
        hard_challenge = CombatChallenge(difficulty=10)
        assert hard_challenge.enemy.health >= 100
        
        # Out of range (should default to reasonable values)
        extreme_challenge = CombatChallenge(difficulty=15)
        assert extreme_challenge.enemy is not None
    
    def test_combat_with_default_stats(self):
        """Test combat works with default player stats."""
        challenge = CombatChallenge(difficulty=2)
        
        # Should work without providing player_stats
        result = challenge.process_response("attack")
        assert isinstance(result, ChallengeResult)
    
    def test_multiple_combat_rounds(self):
        """Test multiple rounds of combat."""
        challenge = CombatChallenge(difficulty=2)
        
        # Simulate several rounds
        for i in range(5):
            result = challenge.process_response("attack")
            if result.success or "Defeat" in result.message:
                break
        
        # Should have progressed through multiple turns
        assert challenge.turn_count > 0
        assert len(challenge.combat_log) > 0