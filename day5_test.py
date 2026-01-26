from world import World
from player import Player

def test_world_creation():
    """Testa criação do mundo"""
    print("=== Teste 1: Criação do Mundo ===")
    world = World()
    
    assert len(world.rooms) == 6
    assert len(world.visited_rooms) == 0
    assert len(world.defeated_enemies) == 0
    print("✅ Mundo criado com 6 salas!\n")


def test_get_room():
    """Testa obter dados de uma sala"""
    print("=== Teste 2: Obter Dados da Sala ===")
    world = World()
    
    room = world.get_room("1")
    assert room is not None
    assert room["type"] == "start"
    assert room["name"] == "Sala Inicial"
    
    print(f"Sala 1: {room['name']}")
    print(f"Tipo: {room['type']}")
    print("✅ Dados da sala obtidos!\n")


def test_room_connections():
    """Testa conexões entre salas"""
    print("=== Teste 3: Conexões entre Salas ===")
    world = World()
    
    # Sala 1 conecta ao sul com sala 2
    connections = world.get_connections("1")
    assert "sul" in connections
    assert connections["sul"] == "2"
    
    # Sala 2 tem 3 conexões
    connections = world.get_connections("2")
    assert len(connections) == 3
    assert "norte" in connections
    assert "leste" in connections
    assert "sul" in connections
    
    print("Sala 2 conecta com:")
    for direction, room_id in connections.items():
        print(f"  {direction} → Sala {room_id}")
    print("✅ Conexões funcionando!\n")


def test_movement():
    """Testa movimentação entre salas"""
    print("=== Teste 4: Movimentação ===")
    world = World()
    player = Player("Arthon")
    
    # Começa na sala 1
    assert player.position == "1"
    print(f"Posição inicial: Sala {player.position}")
    
    # Move para o sul (sala 2)
    new_room = world.move(player.position, "sul")
    assert new_room == "2"
    player.position = new_room
    print(f"Após mover sul: Sala {player.position}")
    
    # Move para leste (sala 3)
    new_room = world.move(player.position, "leste")
    assert new_room == "3"
    player.position = new_room
    print(f"Após mover leste: Sala {player.position}")
    
    # Tenta mover em direção inválida
    new_room = world.move(player.position, "norte")
    assert new_room is None
    print("Tentou mover norte (inválido): None")
    
    print("✅ Movimentação funcionando!\n")


def test_room_description():
    """Testa descrição de salas"""
    print("=== Teste 5: Descrição de Salas ===")
    world = World()
    
    # Obtém descrição da sala inicial
    description = world.get_room_description("1")
    
    assert "Sala Inicial" in description
    assert "1" in world.visited_rooms  # Marca como visitada
    
    print(description)
    print("✅ Descrição exibida e sala marcada como visitada!\n")


def test_enemies():
    """Testa sistema de inimigos"""
    print("=== Teste 6: Sistema de Inimigos ===")
    world = World()
    
    # Sala 3 tem goblin
    assert world.has_enemy("3") == True
    assert world.get_enemy_type("3") == "goblin"
    
    # Sala 5 tem orc chief
    assert world.has_enemy("5") == True
    assert world.get_enemy_type("5") == "orc_chief"
    
    # Sala 1 não tem inimigo
    assert world.has_enemy("1") == False
    
    print("Sala 3: Goblin encontrado")
    print("Sala 5: Orc Chief encontrado")
    print("✅ Sistema de inimigos funcionando!\n")


def test_defeat_enemy():
    """Testa derrotar inimigos"""
    print("=== Teste 7: Derrotar Inimigos ===")
    world = World()
    
    # Antes de derrotar
    assert world.has_enemy("3") == True
    
    # Derrota o inimigo
    world.defeat_enemy("3")
    
    # Depois de derrotar
    assert world.has_enemy("3") == False
    assert "3" in world.defeated_enemies
    
    print("✅ Inimigo derrotado e marcado!\n")


def test_treasure():
    """Testa sistema de tesouros"""
    print("=== Teste 8: Sistema de Tesouros ===")
    world = World()
    
    # Sala 4 tem tesouro
    assert world.has_treasure("4") == True
    
    # Coleta o tesouro
    item = world.get_treasure("4")
    assert item == "health_potion"
    
    # Não pode coletar duas vezes
    assert world.has_treasure("4") == False
    assert "4" in world.looted_rooms
    
    print("Tesouro coletado: health_potion")
    print("✅ Sistema de tesouros funcionando!\n")


def test_enemy_loot():
    """Testa loot de inimigos"""
    print("=== Teste 9: Loot de Inimigos ===")
    world = World()
    
    # Sala 3 tem inimigo e item
    # Mas não pode coletar antes de derrotar
    assert world.has_treasure("3") == False
    
    # Derrota o inimigo
    world.defeat_enemy("3")
    
    # Agora pode coletar
    assert world.has_treasure("3") == True
    item = world.get_treasure("3")
    assert item == "rusty_sword"
    
    print("Inimigo derrotado → Loot disponível")
    print("Loot coletado: rusty_sword")
    print("✅ Loot de inimigos funcionando!\n")


def test_exit_room():
    """Testa sala de saída"""
    print("=== Teste 10: Sala de Saída ===")
    world = World()
    
    # Sala 6 é a saída
    assert world.is_exit("6") == True
    assert world.is_exit("1") == False
    
    # Saída não tem conexões
    connections = world.get_connections("6")
    assert len(connections) == 0
    
    print("Sala 6 identificada como saída")
    print("✅ Sala de saída funcionando!\n")


def test_full_navigation():
    """Testa navegação completa pela dungeon"""
    print("=== Teste 11: Navegação Completa ===")
    world = World()
    player = Player("Arthon")
    
    path = [
        ("sul", "2"),   # Sala 1 → 2
        ("sul", "4"),   # Sala 2 → 4
        ("leste", "5"), # Sala 4 → 5
        ("leste", "6")  # Sala 5 → 6 (saída)
    ]
    
    print(f"Posição inicial: Sala {player.position}")
    
    for direction, expected in path:
        new_room = world.move(player.position, direction)
        assert new_room == expected
        player.position = new_room
        print(f"Move {direction} → Sala {player.position}")
    
    # Chegou na saída
    assert world.is_exit(player.position) == True
    print("\n🎉 Chegou na saída!")
    print("✅ Navegação completa funcionando!\n")


def test_available_directions():
    """Testa obter direções disponíveis"""
    print("=== Teste 12: Direções Disponíveis ===")
    world = World()
    
    directions = world.get_available_directions("2")
    assert len(directions) == 3
    assert "norte" in directions
    assert "leste" in directions
    assert "sul" in directions
    
    print(f"Sala 2 - Direções: {', '.join(directions)}")
    print("✅ Direções disponíveis funcionando!\n")


if __name__ == "__main__":
    print("🎮 TESTES DO DIA 5 - Mapa da Dungeon\n")
    
    test_world_creation()
    test_get_room()
    test_room_connections()
    test_movement()
    test_room_description()
    test_enemies()
    test_defeat_enemy()
    test_treasure()
    test_enemy_loot()
    test_exit_room()
    test_full_navigation()
    test_available_directions()
    
    print("="*50)
    print("✅ TODOS OS TESTES DO DIA 5 CONCLUÍDOS!")
    print("="*50)
