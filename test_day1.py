# test_day1.py - Versão pytest
import pytest
from player import Player
from enemy import Goblin, OrcChief


class TestPlayer:
    """Testes da classe Player"""
    
    def test_player_creation(self):
        """Testa criação do jogador com atributos corretos"""
        player = Player("Arthon")
        
        assert player.name == "Arthon"
        assert player.level == 1
        assert player.xp == 0
        assert player.max_hp == 50
        assert player.hp == 50
        assert player.base_attack == 8
        assert player.base_defense == 3
        assert player.inventory == []
        assert player.position == "1"
        assert player.equipped_weapon is None
        assert player.equipped_shield is None
    
    def test_xp_calculation(self):
        """Testa cálculo de XP necessário"""
        player = Player("Arthon")
        
        assert player.get_xp_needed() == 100  # level 1 * 100
        
        player.level = 2
        assert player.get_xp_needed() == 200  # level 2 * 100
    
    def test_level_up(self, capsys):
        """Testa sistema de level up"""
        player = Player("Arthon")
        initial_attack = player.base_attack
        initial_defense = player.base_defense
        initial_max_hp = player.max_hp
        
        player.gain_xp(100)
        
        assert player.level == 2
        assert player.xp == 0  # XP reseta após level up
        assert player.max_hp == initial_max_hp + 10
        assert player.base_attack == initial_attack + 2
        assert player.base_defense == initial_defense + 1
        assert player.hp == player.max_hp  # HP restaurado
        
        # Verifica se mensagem foi exibida
        captured = capsys.readouterr()
        assert "subiu para o nível 2" in captured.out
    
    def test_multiple_level_ups(self):
        """Testa múltiplos level ups de uma vez"""
        player = Player("Arthon")
        
        player.gain_xp(350)  # Suficiente para level 2 e 3
        
        assert player.level == 3
        assert player.max_hp == 70  # 50 + 10 + 10
        assert player.base_attack == 12  # 8 + 2 + 2
        assert player.base_defense == 5  # 3 + 1 + 1
    
    def test_take_damage(self):
        """Testa sistema de dano"""
        player = Player("Arthon")
        
        player.take_damage(20)
        assert player.hp == 30
        
        player.take_damage(40)  # Mais dano que HP restante
        assert player.hp == 0  # Não deve ficar negativo
    
    def test_heal(self):
        """Testa sistema de cura"""
        player = Player("Arthon")
        player.take_damage(30)
        
        assert player.hp == 20
        
        player.heal(10)
        assert player.hp == 30
        
        player.heal(100)  # Cura excessiva
        assert player.hp == player.max_hp  # Não ultrapassa máximo
    
    def test_is_alive(self):
        """Testa verificação de vida"""
        player = Player("Arthon")
        
        assert player.is_alive() is True
        
        player.take_damage(50)
        assert player.is_alive() is False
    
    def test_inventory_operations(self):
        """Testa adicionar/remover itens do inventário"""
        player = Player("Arthon")
        
        # Cria um mock de item
        class MockItem:
            def __init__(self, name):
                self.name = name
        
        item = MockItem("Espada")
        
        assert len(player.inventory) == 0
        
        player.add_to_inventory(item)
        assert len(player.inventory) == 1
        assert item in player.inventory
        
        player.remove_from_inventory(item)
        assert len(player.inventory) == 0
    
    def test_total_attack_without_weapon(self):
        """Testa ataque total sem arma equipada"""
        player = Player("Arthon")
        
        assert player.get_total_attack() == player.base_attack
    
    def test_total_defense_without_shield(self):
        """Testa defesa total sem escudo equipado"""
        player = Player("Arthon")
        
        assert player.get_total_defense() == player.base_defense


class TestEnemies:
    """Testes das classes de inimigos"""
    
    def test_goblin_creation(self):
        """Testa criação do Goblin"""
        goblin = Goblin()
        
        assert goblin.name == "Goblin"
        assert goblin.hp == 30
        assert goblin.max_hp == 30
        assert goblin.attack == 6
        assert goblin.defense == 2
        assert goblin.xp_reward == 40
        assert goblin.can_flee is True
        assert "goblin" in goblin.description.lower()
    
    def test_orc_chief_creation(self):
        """Testa criação do Orc Chief"""
        boss = OrcChief()
        
        assert boss.name == "Orc Chief"
        assert boss.hp == 80
        assert boss.max_hp == 80
        assert boss.attack == 12
        assert boss.defense == 5
        assert boss.xp_reward == 120
        assert boss.can_flee is False
        assert boss.turn_counter == 0
    
    def test_enemy_take_damage(self):
        """Testa inimigo recebendo dano"""
        goblin = Goblin()
        
        goblin.take_damage(10)
        assert goblin.hp == 20
        
        goblin.take_damage(30)
        assert goblin.hp == 0  # Não fica negativo
    
    def test_enemy_is_alive(self):
        """Testa verificação de vida do inimigo"""
        goblin = Goblin()
        
        assert goblin.is_alive() is True
        
        goblin.take_damage(30)
        assert goblin.is_alive() is False
    
    def test_goblin_attack(self):
        """Testa ataque do Goblin"""
        goblin = Goblin()
        
        damage = goblin.get_attack_damage()
        assert damage == 6
    
    def test_orc_chief_special_attack(self, capsys):
        """Testa habilidade especial do Orc Chief"""
        boss = OrcChief()
        
        # Primeiros 2 turnos: ataque normal
        damage1 = boss.get_attack_damage()
        assert damage1 == 12
        
        damage2 = boss.get_attack_damage()
        assert damage2 == 12
        
        # Turno 3: ataque especial (dobrado)
        damage3 = boss.get_attack_damage()
        assert damage3 == 24
        
        captured = capsys.readouterr()
        assert "ATAQUE PODEROSO" in captured.out
        
        # Turno 4: volta ao normal
        damage4 = boss.get_attack_damage()
        assert damage4 == 12


class TestCombatSimulation:
    """Testes de simulação de combate"""
    
    def test_combat_player_vs_goblin(self):
        """Simula combate completo entre player e goblin"""
        player = Player("Arthon")
        goblin = Goblin()
        
        initial_player_hp = player.hp
        initial_goblin_hp = goblin.hp
        
        max_turns = 20
        turn = 0
        
        while player.is_alive() and goblin.is_alive() and turn < max_turns:
            # Player ataca
            damage_to_enemy = max(1, player.get_total_attack() - goblin.defense)
            goblin.take_damage(damage_to_enemy)
            
            if not goblin.is_alive():
                break
            
            # Goblin ataca
            damage_to_player = max(1, goblin.get_attack_damage() - player.get_total_defense())
            player.take_damage(damage_to_player)
            
            turn += 1
        
        # Player deve vencer (stats são melhores)
        assert not goblin.is_alive()
        assert player.is_alive()
        assert turn < max_turns  # Combate deve terminar antes do limite
    
    def test_xp_gain_after_combat(self):
        """Testa ganho de XP após vencer combate"""
        player = Player("Arthon")
        goblin = Goblin()
        
        initial_xp = player.xp
        
        # Simula vitória
        player.gain_xp(goblin.xp_reward)
        
        assert player.xp == initial_xp + 40


# Fixture para testar com diferentes níveis
@pytest.fixture
def player_level_3():
    """Cria um player de nível 3 para testes"""
    player = Player("Hero")
    player.gain_xp(300)  # Sobe para nível 3
    return player


def test_high_level_player(player_level_3):
    """Testa player de nível alto usando fixture"""
    assert player_level_3.level == 3
    assert player_level_3.max_hp == 70
    assert player_level_3.base_attack == 12


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])