from player import Player
from enemy import Goblin, OrcChief
from combat import Combat
from items import health_potion

def test_combat_creation():
    """Testa criação do combate"""
    print("=== Teste 1: Criação do Combate ===")
    player = Player("Arthon")
    goblin = Goblin()
    
    combat = Combat(player, goblin)
    
    assert combat.player == player
    assert combat.enemy == goblin
    assert combat.turn_count == 0
    assert combat.combat_active == True
    print("✅ Combate criado com sucesso!\n")


def test_damage_calculation():
    """Testa cálculo de dano"""
    print("=== Teste 2: Cálculo de Dano ===")
    player = Player("Arthon")
    goblin = Goblin()
    combat = Combat(player, goblin)
    
    # Player ataque: 13, Goblin defesa: 2
    damage = combat.calculate_damage(player.get_total_attack(), goblin.defense)
    expected = 13 - 2  # 11
    assert damage == expected
    print(f"Dano calculado: {damage} (esperado: {expected})")
    
    # Dano mínimo de 1
    damage = combat.calculate_damage(5, 10)
    assert damage == 1
    print(f"Dano mínimo: {damage}")
    print("✅ Cálculo de dano correto!\n")


def test_player_attack():
    """Testa ataque do jogador"""
    print("=== Teste 3: Ataque do Jogador ===")
    player = Player("Arthon")
    goblin = Goblin()
    combat = Combat(player, goblin)
    
    initial_hp = goblin.hp
    print(f"HP inicial do Goblin: {initial_hp}")
    
    damage = combat.player_attack()
    
    assert goblin.hp == initial_hp - damage
    print(f"HP após ataque: {goblin.hp}")
    print("✅ Ataque do jogador funcionando!\n")


def test_enemy_attack():
    """Testa ataque do inimigo"""
    print("=== Teste 4: Ataque do Inimigo ===")
    player = Player("Arthon")
    goblin = Goblin()
    combat = Combat(player, goblin)
    
    initial_hp = player.hp
    print(f"HP inicial do jogador: {initial_hp}")
    
    damage = combat.enemy_attack()
    
    assert player.hp == initial_hp - damage
    print(f"HP após ataque: {player.hp}")
    print("✅ Ataque do inimigo funcionando!\n")


def test_combat_is_over():
    """Testa detecção de fim de combate"""
    print("=== Teste 5: Fim de Combate ===")
    player = Player("Arthon")
    goblin = Goblin()
    combat = Combat(player, goblin)
    
    # Combate ativo
    assert combat.is_combat_over() == False
    
    # Player morre
    player.hp = 0
    assert combat.is_combat_over() == True
    
    # Reset
    player.hp = 50
    goblin.hp = 0
    assert combat.is_combat_over() == True
    
    print("✅ Detecção de fim de combate funcionando!\n")


def test_combat_result():
    """Testa resultado do combate"""
    print("=== Teste 6: Resultado do Combate ===")
    player = Player("Arthon")
    goblin = Goblin()
    combat = Combat(player, goblin)
    
    # Combate em andamento
    result = combat.get_combat_result()
    assert result == "ongoing"
    print(f"Resultado inicial: {result}")
    
    # Vitória
    goblin.hp = 0
    result = combat.get_combat_result()
    assert result == "victory"
    print(f"Goblin derrotado: {result}")
    
    # Derrota
    player.hp = 0
    goblin.hp = 10
    result = combat.get_combat_result()
    assert result == "defeat"
    print(f"Player derrotado: {result}")
    
    # Fuga
    player.hp = 50
    goblin.hp = 20
    combat.combat_active = False
    result = combat.get_combat_result()
    assert result == "fled"
    print(f"Fugiu do combate: {result}")
    
    print("✅ Resultados de combate corretos!\n")


def test_boss_special_attack():
    """Testa ataque especial do boss"""
    print("=== Teste 7: Ataque Especial do Boss ===")
    player = Player("Arthon")
    boss = OrcChief()
    combat = Combat(player, boss)
    
    print(f"Ataque base do boss: {boss.attack}")
    
    # Primeiros 2 ataques normais
    damage1 = boss.get_attack_damage()
    assert damage1 == boss.attack
    print(f"Turno 1: {damage1} dano")
    
    damage2 = boss.get_attack_damage()
    assert damage2 == boss.attack
    print(f"Turno 2: {damage2} dano")
    
    # Terceiro ataque é especial (dobrado)
    damage3 = boss.get_attack_damage()
    assert damage3 == boss.attack * 2
    print(f"Turno 3 (ESPECIAL): {damage3} dano")
    
    print("✅ Ataque especial do boss funcionando!\n")


def test_flee_from_goblin():
    """Testa fuga do Goblin (pode falhar por ser aleatório)"""
    print("=== Teste 8: Tentativa de Fuga ===")
    player = Player("Arthon")
    goblin = Goblin()
    combat = Combat(player, goblin)
    
    assert goblin.can_flee == True
    print("Goblin permite fuga (10% de chance)")
    
    # Tenta fugir várias vezes
    attempts = 0
    success = False
    max_attempts = 50
    
    for i in range(max_attempts):
        player_test = Player("Test")
        goblin_test = Goblin()
        combat_test = Combat(player_test, goblin_test)
        
        if combat_test.attempt_flee():
            success = True
            attempts = i + 1
            break
    
    if success:
        print(f"✅ Conseguiu fugir após {attempts} tentativas")
    else:
        print(f"⚠️ Não fugiu em {max_attempts} tentativas (normal, é 10%)")
    
    print("✅ Sistema de fuga implementado!\n")


def test_flee_from_boss():
    """Testa que não pode fugir do boss"""
    print("=== Teste 9: Não Pode Fugir do Boss ===")
    player = Player("Arthon")
    boss = OrcChief()
    combat = Combat(player, boss)
    
    assert boss.can_flee == False
    
    # Tenta fugir
    result = combat.attempt_flee()
    
    assert result == False
    assert combat.combat_active == True
    print("✅ Fuga do boss bloqueada corretamente!\n")


def test_simulated_combat():
    """Simula um combate automático completo"""
    print("=== Teste 10: Combate Simulado ===")
    player = Player("Arthon")
    goblin = Goblin()
    combat = Combat(player, goblin)
    
    print(f"{player.name} (HP: {player.hp}) vs {goblin.name} (HP: {goblin.hp})")
    
    turn = 0
    while not combat.is_combat_over() and turn < 20:
        turn += 1
        
        # Player ataca
        combat.player_attack()
        
        if combat.is_combat_over():
            break
        
        # Inimigo ataca
        combat.enemy_attack()
    
    result = combat.get_combat_result()
    print(f"\nCombate terminou em {turn} turnos")
    print(f"Resultado: {result}")
    
    # Player deve vencer (tem stats melhores)
    assert result == "victory"
    assert not goblin.is_alive()
    assert player.is_alive()
    
    print("✅ Combate simulado completo!\n")


def test_xp_gain_after_victory():
    """Testa ganho de XP após vitória"""
    print("=== Teste 11: Ganho de XP ===")
    player = Player("Arthon")
    goblin = Goblin()
    combat = Combat(player, goblin)
    
    initial_xp = player.xp
    expected_xp = goblin.xp_reward
    
    # Derrota o goblin
    goblin.hp = 0
    
    result = combat.end_combat()
    
    assert result["result"] == "victory"
    assert result["xp_gained"] == expected_xp
    assert player.xp == initial_xp + expected_xp
    
    print(f"XP ganho: {expected_xp}")
    print(f"XP total: {player.xp}")
    print("✅ Ganho de XP funcionando!\n")


def test_use_item_in_combat():
    """Testa usar item durante combate"""
    print("=== Teste 12: Usar Item no Combate ===")
    player = Player("Arthon")
    goblin = Goblin()
    combat = Combat(player, goblin)
    
    # Causa dano no player
    player.take_damage(30)
    print(f"HP após dano: {player.hp}/{player.max_hp}")
    
    # Adiciona poção
    player.add_to_inventory(health_potion)
    
    # Usa poção no combate (índice 0)
    initial_hp = player.hp
    success = combat.use_item_in_combat(0)
    
    assert success == True
    assert player.hp > initial_hp  # HP aumentou
    assert len(player.inventory) == 0  # Poção removida
    
    print(f"HP após poção: {player.hp}/{player.max_hp}")
    print("✅ Usar item no combate funcionando!\n")


if __name__ == "__main__":
    print("🎮 TESTES DO DIA 7 - Sistema de Combate\n")
    
    test_combat_creation()
    test_damage_calculation()
    test_player_attack()
    test_enemy_attack()
    test_combat_is_over()
    test_combat_result()
    test_boss_special_attack()
    test_flee_from_goblin()
    test_flee_from_boss()
    test_simulated_combat()
    test_xp_gain_after_victory()
    test_use_item_in_combat()
    
    print("="*50)
    print("✅ TODOS OS TESTES DO DIA 7 CONCLUÍDOS!")
    print("="*50)