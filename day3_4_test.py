from player import Player
from items import rusty_sword, simple_shield, health_potion, Potion, Weapon, Shield

def test_add_items_to_inventory():
    """Testa adicionar itens ao inventário"""
    print("=== Teste 1: Adicionar Itens ao Inventário ===")
    player = Player("Arthon")
    
    assert len(player.inventory) == 0
    
    player.add_to_inventory(rusty_sword)
    player.add_to_inventory(health_potion)
    player.add_to_inventory(simple_shield)
    
    assert len(player.inventory) == 3
    print("✅ Itens adicionados com sucesso!\n")


def test_show_inventory():
    """Testa exibição do inventário"""
    print("=== Teste 2: Exibir Inventário ===")
    player = Player("Arthon")
    
    # Inventário vazio
    player.show_inventory()
    
    # Adiciona itens
    player.add_to_inventory(rusty_sword)
    player.add_to_inventory(health_potion)
    player.add_to_inventory(simple_shield)
    
    # Exibe inventário com itens
    player.show_inventory()
    
    print("✅ Inventário exibido corretamente!\n")


def test_use_potion():
    """Testa usar poção de cura"""
    print("=== Teste 3: Usar Poção de Cura ===")
    player = Player("Arthon")
    
    # Causa dano no player
    player.take_damage(40)
    print(f"HP após dano: {player.hp}/{player.max_hp}")
    
    # Adiciona e usa poção
    player.add_to_inventory(health_potion)
    
    # Usa item no índice 0
    success = player.use_item(0)
    
    assert success == True
    assert len(player.inventory) == 0  # Poção foi removida
    print("✅ Poção usada e removida do inventário!\n")


def test_potion_full_hp():
    """Testa usar poção com HP cheio"""
    print("=== Teste 4: Usar Poção com HP Cheio ===")
    player = Player("Arthon")
    
    # HP já está cheio
    player.add_to_inventory(health_potion)
    
    print(f"HP atual: {player.hp}/{player.max_hp}")
    success = player.use_item(0)
    
    assert success == False  # Não usou
    assert len(player.inventory) == 1  # Poção não foi removida
    print("✅ Poção não foi usada (HP cheio)!\n")


def test_potion_not_exceed_max():
    """Testa que cura não ultrapassa HP máximo"""
    print("=== Teste 5: Cura Não Ultrapassa Máximo ===")
    player = Player("Arthon")
    
    # Causa pouco dano
    player.take_damage(10)
    print(f"HP após dano: {player.hp}/{player.max_hp}")
    
    # Usa poção (cura 30, mas só faltam 10)
    player.add_to_inventory(health_potion)
    player.use_item(0)
    
    assert player.hp == player.max_hp  # HP no máximo
    print("✅ HP não ultrapassou o máximo!\n")


def test_use_non_consumable():
    """Testa tentar usar item não consumível"""
    print("=== Teste 6: Tentar Usar Item Não Consumível ===")
    player = Player("Arthon")
    
    # Adiciona espada (não é consumível)
    player.add_to_inventory(rusty_sword)
    
    success = player.use_item(0)
    
    assert success == False
    assert len(player.inventory) == 1  # Espada continua no inventário
    print("✅ Item não consumível não pode ser usado!\n")


def test_use_invalid_index():
    """Testa usar item com índice inválido"""
    print("=== Teste 7: Índice Inválido ===")
    player = Player("Arthon")
    
    player.add_to_inventory(health_potion)
    
    # Tenta usar índice inexistente
    success = player.use_item(5)
    
    assert success == False
    assert len(player.inventory) == 1  # Inventário intacto
    print("✅ Índice inválido tratado corretamente!\n")


def test_multiple_potions():
    """Testa usar múltiplas poções"""
    print("=== Teste 8: Múltiplas Poções ===")
    player = Player("Arthon")
    
    # Causa muito dano
    player.take_damage(70)
    print(f"HP após dano: {player.hp}/{player.max_hp}")
    
    # Adiciona 3 poções
    for _ in range(3):
        player.add_to_inventory(Potion("Poção de Cura", 30, "Cura 30 HP"))
    
    print(f"Inventário: {len(player.inventory)} poções")
    
    # Usa primeira poção
    player.use_item(0)
    assert len(player.inventory) == 2
    
    # Usa segunda poção
    player.use_item(0)
    assert len(player.inventory) == 1
    
    # HP deve estar restaurado (ou próximo do máximo)
    print(f"HP final: {player.hp}/{player.max_hp}")
    print("✅ Múltiplas poções funcionam!\n")


def test_inventory_with_equipment():
    """Testa inventário com equipamentos e consumíveis"""
    print("=== Teste 9: Inventário Misto ===")
    player = Player("Arthon")
    
    # Adiciona vários tipos de itens
    player.add_to_inventory(rusty_sword)
    player.add_to_inventory(health_potion)
    player.add_to_inventory(simple_shield)
    player.add_to_inventory(Potion("Poção Pequena", 15, "Cura 15 HP"))
    
    player.show_inventory()
    
    assert len(player.inventory) == 4
    
    # Equipa espada (não remove do inventário)
    player.equip_weapon(rusty_sword)
    
    # Usa poção (remove do inventário)
    player.take_damage(20)
    player.use_item(1)  # Segunda posição (health_potion)
    
    assert len(player.inventory) == 3  # Uma poção foi removida
    print("✅ Inventário misto funciona corretamente!\n")


if __name__ == "__main__":
    print("🎮 TESTES DOS DIAS 3 e 4 - Sistema de Itens\n")
    
    test_add_items_to_inventory()
    test_show_inventory()
    test_use_potion()
    test_potion_full_hp()
    test_potion_not_exceed_max()
    test_use_non_consumable()
    test_use_invalid_index()
    test_multiple_potions()
    test_inventory_with_equipment()
    
    print("="*50)
    print("✅ TODOS OS TESTES DOS DIAS 3 e 4 CONCLUÍDOS!")
    print("="*50)
