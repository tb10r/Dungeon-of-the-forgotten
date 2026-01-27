from player import Player
from world import World
from enemy import Goblin, OrcChief
from items import health_potion

def test_create_enemy():
    """Testa criação de inimigo a partir da sala"""
    print("=== Teste 1: Criar Inimigo da Sala ===")
    world = World()
    
    # Sala 3 tem goblin
    enemy = world.create_enemy("3")
    assert enemy is not None
    assert enemy.name == "Goblin"
    print(f"Sala 3: {enemy.name} criado")
    
    # Sala 5 tem orc chief
    enemy = world.create_enemy("5")
    assert enemy is not None
    assert enemy.name == "Orc Chief"
    print(f"Sala 5: {enemy.name} criado")
    
    # Sala 1 não tem inimigo
    enemy = world.create_enemy("1")
    assert enemy is None
    print("Sala 1: Sem inimigo")
    
    print("✅ Criação de inimigos funcionando!\n")


def test_get_item_from_room():
    """Testa obter item da sala"""
    print("=== Teste 2: Obter Item da Sala ===")
    world = World()
    
    # Sala 4 tem poção
    item = world.get_item_from_room("4")
    assert item is not None
    assert item.name == "Poção de Cura"
    print(f"Sala 4: {item.name}")
    
    # Não pode coletar duas vezes
    item2 = world.get_item_from_room("4")
    assert item2 is None
    print("Sala 4: Já coletado (None)")
    
    print("✅ Obter itens funcionando!\n")


def test_room_with_treasure_only():
    """Testa sala apenas com tesouro (sem inimigo)"""
    print("=== Teste 3: Sala com Tesouro ===")
    world = World()
    player = Player("Arthon")
    
    # Move para sala 4 (tesouro)
    player.position = "4"
    
    initial_inventory = len(player.inventory)
    
    result = world.process_room_events(player)
    
    assert result["event"] == "treasure"
    assert result["item"] == "Poção de Cura"  # Nome do item, não o identificador
    assert len(player.inventory) == initial_inventory + 1
    
    print(f"Item coletado: {result['item']}")
    print("✅ Sala de tesouro funcionando!\n")


def test_room_with_enemy():
    """Testa sala com inimigo (combate automático)"""
    print("=== Teste 4: Sala com Inimigo ===")
    print("⚠️  Este teste requer interação manual (será pulado)\n")
    # Não podemos testar automaticamente porque run_combat() pede input
    print("✅ Teste manual necessário!\n")


def test_enemy_loot_integration():
    """Testa que loot só aparece após derrotar inimigo"""
    print("=== Teste 5: Loot de Inimigo ===")
    world = World()
    player = Player("Arthon")
    
    # Sala 3 tem goblin e espada
    player.position = "3"
    
    # Antes de derrotar, não há tesouro disponível
    assert world.has_treasure("3") == False
    
    # Derrota o inimigo manualmente
    world.defeat_enemy("3")
    
    # Agora o tesouro está disponível
    assert world.has_treasure("3") == True
    
    # Coleta o loot
    item = world.get_item_from_room("3")
    assert item is not None
    assert item.name == "Espada Enferrujada"
    
    print(f"Inimigo derrotado → Loot disponível: {item.name}")
    print("✅ Loot de inimigo funcionando!\n")


def test_exit_room_detection():
    """Testa detecção da sala de saída"""
    print("=== Teste 6: Detecção de Saída ===")
    world = World()
    player = Player("Arthon")
    
    # Move para sala 6 (saída)
    player.position = "6"
    
    result = world.process_room_events(player)
    
    assert result["event"] == "exit"
    
    print("Sala 6 identificada como saída")
    print("✅ Detecção de saída funcionando!\n")


def test_empty_room():
    """Testa sala sem eventos"""
    print("=== Teste 7: Sala Vazia ===")
    world = World()
    player = Player("Arthon")
    
    # Sala 2 (corredor) não tem nada após visitar
    player.position = "2"
    
    result = world.process_room_events(player)
    
    assert result["event"] == "none"
    
    print("Sala 2: Sem eventos")
    print("✅ Sala vazia funcionando!\n")


def test_revisit_defeated_enemy_room():
    """Testa revisitar sala onde inimigo foi derrotado"""
    print("=== Teste 8: Revisitar Sala ===")
    world = World()
    player = Player("Arthon")
    
    # Sala 3 tem inimigo
    player.position = "3"
    
    # Derrota inimigo
    world.defeat_enemy("3")
    
    # Coleta loot
    item = world.get_item_from_room("3")
    assert item is not None
    
    # Revisita a sala
    result = world.process_room_events(player)
    
    # Não deve ter mais eventos
    assert result["event"] == "none"
    
    print("Sala revisitada: Sem eventos (inimigo já derrotado)")
    print("✅ Revisita funcionando!\n")


def test_navigation_with_events():
    """Testa navegação coletando tesouros"""
    print("=== Teste 9: Navegação com Eventos ===")
    world = World()
    player = Player("Arthon")
    
    print(f"Posição inicial: Sala {player.position}")
    
    # Move para sala 2
    new_pos = world.move(player.position, "sul")
    player.position = new_pos
    print(f"Move sul → Sala {player.position}")
    world.process_room_events(player)
    
    # Move para sala 4 (tesouro)
    new_pos = world.move(player.position, "sul")
    player.position = new_pos
    print(f"Move sul → Sala {player.position}")
    
    initial_inventory = len(player.inventory)
    result = world.process_room_events(player)
    
    assert result["event"] == "treasure"
    assert len(player.inventory) > initial_inventory
    
    print(f"Tesouro coletado na sala {player.position}")
    print("✅ Navegação com eventos funcionando!\n")


def test_multiple_items_collection():
    """Testa coletar múltiplos itens"""
    print("=== Teste 10: Coletar Múltiplos Itens ===")
    world = World()
    player = Player("Arthon")
    
    initial_count = len(player.inventory)
    
    # Coleta tesouro da sala 4
    player.position = "4"
    world.process_room_events(player)
    assert len(player.inventory) == initial_count + 1
    
    # Derrota inimigo e coleta loot da sala 3
    player.position = "3"
    world.defeat_enemy("3")
    item = world.get_item_from_room("3")
    if item:
        player.add_to_inventory(item)
    
    assert len(player.inventory) == initial_count + 2
    
    player.show_inventory()
    print("✅ Múltiplos itens coletados!\n")


def test_world_state_persistence():
    """Testa que o estado do mundo persiste"""
    print("=== Teste 11: Persistência de Estado ===")
    world = World()
    player = Player("Arthon")
    
    # Derrota inimigo da sala 3
    world.defeat_enemy("3")
    assert "3" in world.defeated_enemies
    
    # Coleta tesouro da sala 4
    player.position = "4"
    world.process_room_events(player)
    assert "4" in world.looted_rooms
    
    # Verifica status
    world.show_map_status()
    
    assert len(world.defeated_enemies) >= 1
    assert len(world.looted_rooms) >= 1
    
    print("✅ Estado persistente!\n")


if __name__ == "__main__":
    print("🎮 TESTES DO DIA 8 - Integração Combate + Mundo\n")
    
    test_create_enemy()
    test_get_item_from_room()
    test_room_with_treasure_only()
    test_room_with_enemy()
    test_enemy_loot_integration()
    test_exit_room_detection()
    test_empty_room()
    test_revisit_defeated_enemy_room()
    test_navigation_with_events()
    test_multiple_items_collection()
    test_world_state_persistence()
    
    print("="*50)
    print("✅ TODOS OS TESTES DO DIA 8 CONCLUÍDOS!")
    print("="*50)
    print("\n⚠️  Nota: Teste 4 requer interação manual")
    print("Para testar combate completo, rode o game.py quando estiver pronto!")