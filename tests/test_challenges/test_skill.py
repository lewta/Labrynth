"""Tests for SkillChallenge class."""

import pytest
from unittest.mock import patch
from src.challenges.skill import SkillChallenge
from src.utils.data_models import Item, ChallengeResult, PlayerStats


class TestSkillChallenge:
    """Test cases for SkillChallenge class."""
    
    def test_skill_challenge_initialization_default(self):
        """Test skill challenge initialization with default parameters."""
        challenge = SkillChallenge(difficulty=5)
        
        assert challenge.difficulty == 5
        assert challenge.skill_type in SkillChallenge.SKILL_TYPES
        assert challenge.attempts == 0
        assert challenge.max_attempts == 3
        assert challenge.reward_item is not None
        assert challenge.challenge_scenario is not None
    
    def test_skill_challenge_initialization_specific_skill(self):
        """Test skill challenge initialization with specific skill type."""
        challenge = SkillChallenge(difficulty=3, skill_type='strength')
        
        assert challenge.skill_type == 'strength'
        assert challenge.name == 'Strength Challenge'
        assert 'physical' in challenge.description.lower()
    
    def test_invalid_skill_type(self):
        """Test initialization with invalid skill type raises error."""
        with pytest.raises(ValueError, match="Invalid skill type"):
            SkillChallenge(difficulty=5, skill_type='invalid_skill')
    
    def test_custom_reward(self):
        """Test skill challenge with custom reward."""
        custom_reward = Item("Test Enhancement", "A test item", "enhancement", 50)
        challenge = SkillChallenge(difficulty=5, reward_item=custom_reward)
        
        assert challenge.reward_item == custom_reward
    
    def test_success_threshold_calculation(self):
        """Test success threshold scales with difficulty."""
        easy_challenge = SkillChallenge(difficulty=1)
        hard_challenge = SkillChallenge(difficulty=10)
        
        assert hard_challenge.success_threshold > easy_challenge.success_threshold
        assert easy_challenge.success_threshold >= 30  # Minimum reasonable threshold
        assert hard_challenge.success_threshold <= 80  # Maximum threshold cap
    
    def test_present_challenge_initial(self):
        """Test initial challenge presentation."""
        challenge = SkillChallenge(difficulty=5, skill_type='intelligence')
        presentation = challenge.present_challenge()
        
        assert "Intelligence Challenge" in presentation
        assert "Difficulty: 5/10" in presentation
        assert "Primary Stat: Intelligence" in presentation
        assert challenge.challenge_scenario['action'] in presentation
        assert "examine" in presentation
    
    def test_present_challenge_with_attempts(self):
        """Test challenge presentation after some attempts."""
        challenge = SkillChallenge(difficulty=5, skill_type='dexterity')
        challenge.attempts = 1
        
        presentation = challenge.present_challenge()
        
        assert "Attempts remaining: 2" in presentation
    
    def test_examine_action(self):
        """Test examine action provides hints."""
        challenge = SkillChallenge(difficulty=5, skill_type='strength')
        
        # Test with high stats
        high_stats = PlayerStats(strength=18)
        result = challenge.process_response("examine", high_stats)
        
        assert result.success is False  # Examine doesn't complete challenge
        assert "confident" in result.message.lower()
        
        # Test with low stats
        low_stats = PlayerStats(strength=5)
        result = challenge.process_response("examine", low_stats)
        
        assert "difficult" in result.message.lower()
    
    def test_invalid_action(self):
        """Test invalid action response."""
        challenge = SkillChallenge(difficulty=5, skill_type='luck')
        result = challenge.process_response("invalid_action")
        
        assert result.success is False
        assert "Invalid action" in result.message
        assert challenge.challenge_scenario['action'] in result.message
    
    @patch('random.randint')
    def test_successful_attempt(self, mock_random):
        """Test successful skill challenge attempt."""
        challenge = SkillChallenge(difficulty=3, skill_type='intelligence')
        player_stats = PlayerStats(intelligence=15)
        
        # Mock a successful roll (low number for success)
        mock_random.return_value = 20
        
        result = challenge.process_response(challenge.challenge_scenario['action'], player_stats)
        
        assert result.success is True
        assert "solve" in result.message.lower() or "overcome" in result.message.lower()
        assert result.reward is not None
        assert challenge.completed is True
    
    @patch('random.randint')
    def test_failed_attempt_with_retries(self, mock_random):
        """Test failed attempt with remaining retries."""
        challenge = SkillChallenge(difficulty=8, skill_type='dexterity')
        player_stats = PlayerStats(dexterity=8)
        
        # Mock a failed roll (high number for failure)
        mock_random.return_value = 90
        
        result = challenge.process_response(challenge.challenge_scenario['action'], player_stats)
        
        assert result.success is False
        assert challenge.attempts == 1
        assert "attempt(s) remaining" in result.message
        assert challenge.completed is False
    
    @patch('random.randint')
    def test_final_failure(self, mock_random):
        """Test final failure after all attempts used."""
        challenge = SkillChallenge(difficulty=9, skill_type='strength')
        challenge.attempts = 2  # Set to 2 so next attempt is final
        player_stats = PlayerStats(strength=6)
        
        # Mock failed roll and damage calculation
        mock_random.side_effect = [95, 2]  # Failed roll, then damage variance
        
        result = challenge.process_response(challenge.challenge_scenario['action'], player_stats)
        
        assert result.success is False
        assert result.damage > 0
        assert challenge.attempts == 3
        assert "best efforts" in result.message or "proves too" in result.message
    
    def test_success_chance_calculation(self):
        """Test success chance calculation with different stats."""
        challenge = SkillChallenge(difficulty=5, skill_type='luck')
        
        # Test with average stats (10)
        average_chance = challenge._calculate_success_chance(10)
        assert 30 <= average_chance <= 70  # Should be around 50% base
        
        # Test with high stats
        high_chance = challenge._calculate_success_chance(18)
        assert high_chance > average_chance
        
        # Test with low stats
        low_chance = challenge._calculate_success_chance(5)
        assert low_chance < average_chance
        
        # Test bounds
        extreme_high_chance = challenge._calculate_success_chance(25)
        extreme_low_chance = challenge._calculate_success_chance(1)
        assert 5 <= extreme_low_chance <= 95
        assert 5 <= extreme_high_chance <= 95
    
    def test_difficulty_affects_success_chance(self):
        """Test that difficulty affects success chance."""
        easy_challenge = SkillChallenge(difficulty=1, skill_type='intelligence')
        hard_challenge = SkillChallenge(difficulty=10, skill_type='intelligence')
        
        # Same stats, different difficulty
        stats = PlayerStats(intelligence=12)
        
        easy_chance = easy_challenge._calculate_success_chance(12)
        hard_chance = hard_challenge._calculate_success_chance(12)
        
        assert easy_chance > hard_chance
    
    def test_get_reward_when_completed(self):
        """Test getting reward when challenge is completed."""
        challenge = SkillChallenge(difficulty=5, skill_type='dexterity')
        challenge.mark_completed()
        
        reward = challenge.get_reward()
        assert reward is not None
        assert reward.item_type == "enhancement"
    
    def test_get_reward_when_not_completed(self):
        """Test getting reward when challenge is not completed."""
        challenge = SkillChallenge(difficulty=5, skill_type='strength')
        
        reward = challenge.get_reward()
        assert reward is None
    
    def test_reset_challenge(self):
        """Test resetting the skill challenge."""
        challenge = SkillChallenge(difficulty=5, skill_type='luck')
        original_scenario = challenge.challenge_scenario.copy()
        
        # Simulate some attempts
        challenge.attempts = 2
        challenge.mark_completed()
        
        # Reset
        challenge.reset()
        
        assert challenge.attempts == 0
        assert challenge.completed is False
        # Scenario should be regenerated (might be different)
        assert challenge.challenge_scenario is not None
    
    def test_get_challenge_info(self):
        """Test getting challenge information."""
        challenge = SkillChallenge(difficulty=7, skill_type='intelligence')
        challenge.attempts = 1
        
        info = challenge.get_challenge_info()
        
        assert info["skill_type"] == "intelligence"
        assert info["difficulty"] == 7
        assert info["attempts"] == 1
        assert info["max_attempts"] == 3
        assert "scenario" in info
        assert "completed" in info
    
    def test_get_success_chance_for_stats(self):
        """Test getting success chance for specific stats."""
        challenge = SkillChallenge(difficulty=5, skill_type='strength')
        stats = PlayerStats(strength=14)
        
        chance = challenge.get_success_chance_for_stats(stats)
        
        assert isinstance(chance, int)
        assert 0 <= chance <= 100
    
    def test_all_skill_types_work(self):
        """Test that all skill types can be created and work."""
        for skill_type in SkillChallenge.SKILL_TYPES.keys():
            challenge = SkillChallenge(difficulty=5, skill_type=skill_type)
            
            assert challenge.skill_type == skill_type
            assert challenge.name == SkillChallenge.SKILL_TYPES[skill_type]['name']
            
            # Test presentation works
            presentation = challenge.present_challenge()
            assert skill_type.title() in presentation
            
            # Test examine works
            result = challenge.process_response("examine")
            assert isinstance(result, ChallengeResult)
    
    def test_default_stats_handling(self):
        """Test challenge works with default player stats."""
        challenge = SkillChallenge(difficulty=5, skill_type='dexterity')
        
        # Should work without providing player_stats
        result = challenge.process_response("examine")
        assert isinstance(result, ChallengeResult)
        
        result = challenge.process_response(challenge.challenge_scenario['action'])
        assert isinstance(result, ChallengeResult)
    
    def test_reward_scaling_with_difficulty(self):
        """Test that rewards scale with difficulty."""
        easy_challenge = SkillChallenge(difficulty=1, skill_type='strength')
        hard_challenge = SkillChallenge(difficulty=10, skill_type='strength')
        
        assert hard_challenge.reward_item.value > easy_challenge.reward_item.value
    
    def test_different_skill_types_have_different_rewards(self):
        """Test that different skill types have appropriate rewards."""
        strength_challenge = SkillChallenge(difficulty=5, skill_type='strength')
        intelligence_challenge = SkillChallenge(difficulty=5, skill_type='intelligence')
        dexterity_challenge = SkillChallenge(difficulty=5, skill_type='dexterity')
        luck_challenge = SkillChallenge(difficulty=5, skill_type='luck')
        
        # Rewards should be different and thematically appropriate
        rewards = [
            strength_challenge.reward_item.name,
            intelligence_challenge.reward_item.name,
            dexterity_challenge.reward_item.name,
            luck_challenge.reward_item.name
        ]
        
        # All should be different
        assert len(set(rewards)) == 4
        
        # Should contain thematically appropriate words
        assert any(word in strength_challenge.reward_item.name.lower() 
                  for word in ['power', 'strength', 'might', 'gauntlets', 'belt'])
        assert any(word in intelligence_challenge.reward_item.name.lower() 
                  for word in ['wisdom', 'knowledge', 'scholar', 'mind'])


class TestSkillChallengeEdgeCases:
    """Test edge cases for SkillChallenge."""
    
    def test_extreme_difficulty_levels(self):
        """Test skill challenge with extreme difficulty levels."""
        # Very easy
        easy_challenge = SkillChallenge(difficulty=1, skill_type='luck')
        assert easy_challenge.success_threshold <= 35
        
        # Very hard
        hard_challenge = SkillChallenge(difficulty=10, skill_type='luck')
        assert hard_challenge.success_threshold >= 70
    
    @patch('random.randint')
    def test_damage_calculation_variance(self, mock_random):
        """Test damage calculation has appropriate variance."""
        challenge = SkillChallenge(difficulty=5, skill_type='strength')
        
        # Test different variance values
        mock_random.return_value = -2  # Minimum variance
        damage1 = challenge._calculate_failure_damage()
        
        mock_random.return_value = 3   # Maximum variance
        damage2 = challenge._calculate_failure_damage()
        
        assert damage1 >= 1  # Always at least 1 damage
        assert damage2 >= damage1  # Higher variance should give more damage
        assert damage2 <= 20  # Reasonable maximum
    
    def test_success_message_quality_scaling(self):
        """Test success messages scale with roll quality."""
        challenge = SkillChallenge(difficulty=5, skill_type='dexterity')
        
        # Test different roll qualities
        excellent_msg = challenge._get_success_message(5, 60)  # Very low roll
        good_msg = challenge._get_success_message(25, 60)      # Medium roll
        barely_msg = challenge._get_success_message(55, 60)    # High roll
        
        # Messages should be different
        assert excellent_msg != good_msg != barely_msg
        
        # Should contain quality indicators
        assert "masterfully" in excellent_msg or "skillfully" in excellent_msg
    
    def test_failure_message_quality_scaling(self):
        """Test failure messages scale with how badly player failed."""
        challenge = SkillChallenge(difficulty=5, skill_type='intelligence')
        
        # Test different failure qualities
        close_msg = challenge._get_failure_message(65, 60, 2)  # Close failure
        bad_msg = challenge._get_failure_message(95, 60, 2)    # Bad failure
        
        # Messages should be different
        assert close_msg != bad_msg
        
        # Should contain appropriate quality indicators
        assert ("narrowly" in close_msg or "poorly" in close_msg or 
                "badly" in bad_msg)
    
    @patch('random.choice')
    def test_scenario_generation_randomness(self, mock_choice):
        """Test that scenario generation uses randomness appropriately."""
        # Mock random choices to ensure deterministic testing
        mock_choice.side_effect = ["Test scenario", "test_action"]
        
        challenge = SkillChallenge(difficulty=5, skill_type='strength')
        
        # Verify random.choice was called for scenario generation
        assert mock_choice.call_count >= 2  # At least for scenario and action
    
    def test_multiple_attempts_tracking(self):
        """Test that attempts are tracked correctly across multiple tries."""
        challenge = SkillChallenge(difficulty=8, skill_type='luck')
        stats = PlayerStats(luck=5)  # Low luck for likely failures
        
        initial_attempts = challenge.attempts
        
        # Make an attempt (likely to fail with low luck and high difficulty)
        with patch('random.randint', return_value=95):  # Force failure
            result = challenge.process_response(challenge.challenge_scenario['action'], stats)
        
        assert challenge.attempts == initial_attempts + 1
        assert not result.success
    
    def test_challenge_scenario_contains_required_fields(self):
        """Test that generated scenarios contain all required fields."""
        for skill_type in SkillChallenge.SKILL_TYPES.keys():
            challenge = SkillChallenge(difficulty=5, skill_type=skill_type)
            scenario = challenge.challenge_scenario
            
            assert 'scenario' in scenario
            assert 'action' in scenario
            assert 'stat' in scenario
            assert scenario['stat'] == skill_type
            assert isinstance(scenario['scenario'], str)
            assert isinstance(scenario['action'], str)
            assert len(scenario['scenario']) > 0
            assert len(scenario['action']) > 0