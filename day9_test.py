from player import Player
from world import World
from save_manager import SaveManager
from items import rusty_sword, health_potion
import os


def test_save_manager_creation():
    """Testa criação do SaveManager"""
    print("=== Teste 1: Criação do SaveManager ===")
    
    save_mgr = SaveManager()
    
    # Verifica se pasta foi criada
    assert os.path.exists("saves")
    print("✅ Pasta 'saves' criada!")
    print("✅ SaveManager criado com sucesso!\n")


def test_save_game():
    """Testa salvar jogo"""
    print("=== Teste 2: Salvar Jogo ===")
    
    save_mgr = SaveManager()
    player = Player("Arthon")
    world = World()
    
    # Modifica estado do player
    player.gain_xp(50)
    player.take_damage(20)
    player.add_to_inventory(rusty_sword)
    player.position = "3"
    
    # Modifica estado do world
    world.defeat_enemy("3")
    
    # Salva
    filepath = save_mgr.save_game(player, world, "test_save.json")
    
    assert filepath is not None
    assert os.path.exists(filepath)
    print("✅ Jogo salvo com sucesso!\n")


def test_load_game():
    """Testa carregar jogo"""
    print("=== Teste 3: Carregar Jogo ===")
    
    save_mgr = SaveManager()
    
    # Primeiro salva um jogo
    player = Player("Arthon")
    world = World()
    
    player.level = 2
    player.xp = 50
    player.strength = 6
    player.vitality = 6
    player.agility = 5
    player.max_hp = player.calculate_max_hp()
    player.hp = player.max_hp
    player.base_attack = player.calculate_attack()
    player.base_defense = player.calculate_defense()
    player.add_to_inventory(rusty_sword)
    player.add_to_inventory(health_potion)
    player.position = "4"
    
    world.defeat_enemy("3")
    world.visited_rooms.add("1")
    world.visited_rooms.add("2")
    
    save_mgr.save_game(player, world, "test_load.json")
    
    # Agora carrega
    loaded_player, loaded_world = save_mgr.load_game("test_load.json")
    
    assert loaded_player is not None
    assert loaded_world is not None
    assert loaded_player.name == "Arthon"
    assert loaded_player.level == 2  # Subiu de nível
    assert len(loaded_player.inventory) == 2
    assert loaded_player.position == "4"
    assert "3" in loaded_world.defeated_enemies
    
    print(f"Player carregado: {loaded_player.name}")
    print(f"Nível: {loaded_player.level}")
    print(f"Posição: Sala {loaded_player.position}")
    print(f"Inventário: {len(loaded_player.inventory)} itens")
    print("✅ Jogo carregado com sucesso!\n")


def test_save_with_equipment():
    """Testa salvar com equipamentos"""
    print("=== Teste 4: Salvar com Equipamentos ===")
    
    save_mgr = SaveManager()
    player = Player("Arthon")
    world = World()
    
    # Adiciona e equipa itens
    player.add_to_inventory(rusty_sword)
    player.equip_weapon(rusty_sword)
    
    # Salva
    save_mgr.save_game(player, world, "test_equipment.json")
    
    # Carrega
    loaded_player, loaded_world = save_mgr.load_game("test_equipment.json")
    
    assert loaded_player.equipped_weapon is not None
    assert loaded_player.equipped_weapon.name == "Espada Enferrujada"
    assert loaded_player.get_total_attack() > loaded_player.base_attack
    
    print(f"Arma equipada: {loaded_player.equipped_weapon.name}")
    print(f"Ataque total: {loaded_player.get_total_attack()}")
    print("✅ Equipamentos salvos/carregados!\n")


def test_list_saves():
    """Testa listar saves"""
    print("=== Teste 5: Listar Saves ===")
    
    save_mgr = SaveManager()
    
    # Cria alguns saves
    for i in range(3):
        player = Player(f"Player{i}")
        world = World()
        save_mgr.save_game(player, world, f"test_list_{i}.json")
    
    # Lista
    saves = save_mgr.list_saves()
    
    assert len(saves) >= 3
    
    save_mgr.show_save_list()
    
    print(f"✅ {len(saves)} saves encontrados!\n")


def test_save_nonexistent():
    """Testa carregar save inexistente"""
    print("=== Teste 6: Save Inexistente ===")
    
    save_mgr = SaveManager()
    
    player, world = save_mgr.load_game("nao_existe.json")
    
    assert player is None
    assert world is None
    print("✅ Save inexistente tratado corretamente!\n")


def test_save_exists():
    """Testa verificar se save existe"""
    print("=== Teste 7: Verificar Existência ===")
    
    save_mgr = SaveManager()
    player = Player("Test")
    world = World()
    
    save_mgr.save_game(player, world, "test_exists.json")
    
    assert save_mgr.save_exists("test_exists.json") == True
    assert save_mgr.save_exists("nao_existe.json") == False
    
    print("✅ Verificação de existência funcionando!\n")


def test_delete_save():
    """Testa deletar save"""
    print("=== Teste 8: Deletar Save ===")
    
    save_mgr = SaveManager()
    player = Player("ToDelete")
    world = World()
    
    # Cria save
    save_mgr.save_game(player, world, "test_delete.json")
    assert save_mgr.save_exists("test_delete.json")
    
    # Deleta
    result = save_mgr.delete_save("test_delete.json")
    
    assert result == True
    assert not save_mgr.save_exists("test_delete.json")
    
    print("✅ Save deletado com sucesso!\n")


def test_save_complex_state():
    """Testa salvar estado complexo"""
    print("=== Teste 9: Estado Complexo ===")
    
    save_mgr = SaveManager()
    player = Player("Complex")
    world = World()
    
    # Estado bem avançado
    player.level = 3
    player.xp = 50
    player.strength = 7
    player.vitality = 7
    player.agility = 6
    player.max_hp = player.calculate_max_hp()
    player.hp = player.max_hp
    player.base_attack = player.calculate_attack()
    player.base_defense = player.calculate_defense()
    player.position = "5"
    
    player.add_to_inventory(rusty_sword)
    player.add_to_inventory(health_potion)
    player.equip_weapon(rusty_sword)
    
    world.defeat_enemy("3")
    world.defeat_enemy("5")
    world.looted_rooms.add("4")
    world.visited_rooms = {"1", "2", "3", "4", "5"}
    
    # Salva e carrega
    save_mgr.save_game(player, world, "test_complex.json")
    loaded_player, loaded_world = save_mgr.load_game("test_complex.json")
    
    assert loaded_player.level == 3
    assert loaded_player.position == "5"
    assert len(loaded_world.defeated_enemies) == 2
    assert len(loaded_world.visited_rooms) == 5
    
    loaded_player.show_status()
    loaded_world.show_map_status()
    
    print("✅ Estado complexo salvo/carregado!\n")


def cleanup_test_saves():
    """Limpa saves de teste"""
    print("=== Limpando Saves de Teste ===")
    
    save_mgr = SaveManager()
    test_files = [
        "test_save.json",
        "test_load.json",
        "test_equipment.json",
        "test_list_0.json",
        "test_list_1.json",
        "test_list_2.json",
        "test_exists.json",
        "test_complex.json"
    ]
    
    for filename in test_files:
        if save_mgr.save_exists(filename):
            save_mgr.delete_save(filename)
    
    print("✅ Saves de teste removidos!\n")


if __name__ == "__main__":
    print("🎮 TESTES DO DIA 9 - Sistema de Save/Load\n")
    
    test_save_manager_creation()
    test_save_game()
    test_load_game()
    test_save_with_equipment()
    test_list_saves()
    test_save_nonexistent()
    test_save_exists()
    test_delete_save()
    test_save_complex_state()
    
    # Limpa arquivos de teste
    cleanup_test_saves()
    
    print("="*50)
    print("✅ TODOS OS TESTES DO DIA 9 CONCLUÍDOS!")
    print("="*50)