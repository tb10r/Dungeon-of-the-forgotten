from player import Player
from world import World
from save_manager import SaveManager
from minimap import MiniMap
import sys


def clear_screen():
    """Limpa a tela (multiplataforma)"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def show_title():
    """Exibe título do jogo"""
    print("\n" + "="*60)
    print("       🗡️  DUNGEON OF THE FORGOTTEN  🗡️")
    print("="*60)


def manage_saves_menu(save_mgr):
    """Menu para gerenciar saves"""
    while True:
        show_title()
        print("\n💾 GERENCIAR SAVES\n")
        print("1 - Ver Saves")
        print("2 - Deletar Save")
        print("0 - Voltar")
        
        choice = input("\nEscolha: ").strip()
        
        if choice == "1":
            save_mgr.show_save_list()
            input("\n[Pressione Enter para continuar]")
        
        elif choice == "2":
            saves = save_mgr.list_saves()
            
            if not saves:
                print("\n❌ Nenhum save encontrado!")
                input("[Pressione Enter para continuar]")
                continue
            
            save_mgr.show_save_list()
            
            try:
                idx = int(input("\nQual save deletar? (0 para cancelar): "))
                
                if idx == 0:
                    continue
                
                if 1 <= idx <= len(saves):
                    filename = saves[idx - 1]['filename']
                    
                    # Confirmação
                    print(f"\n⚠️  Tem certeza que deseja deletar '{filename}'?")
                    confirm = input("Digite 'SIM' para confirmar: ").strip().upper()
                    
                    if confirm == "SIM":
                        save_mgr.delete_save(filename)
                    else:
                        print("\n❌ Operação cancelada!")
                else:
                    print("\n❌ Opção inválida!")
            
            except ValueError:
                print("\n❌ Opção inválida!")
            
            input("\n[Pressione Enter para continuar]")
        
        elif choice == "0":
            break
        
        else:
            print("\n❌ Opção inválida!")
            input("[Pressione Enter para continuar]")
def main_menu():
    """Menu principal do jogo"""
    save_mgr = SaveManager()
    
    while True:
        show_title()
        print("\n📜 MENU PRINCIPAL\n")
        print("1 - Novo Jogo")
        print("2 - Carregar Jogo")
        print("3 - Ver Saves")
        print("4 - Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            return start_new_game()
        
        elif choice == "2":
            result = load_game_menu(save_mgr)
            if result:
                return result
        
        elif choice == "3":
            manage_saves_menu(save_mgr)
        
        elif choice == "4":
            print("\n👋 Até logo!")
            sys.exit(0)
        
        else:
            print("\n❌ Opção inválida!")
            input("[Pressione Enter para continuar]")


def start_new_game():
    """Inicia um novo jogo"""
    show_title()
    print("\n⚔️  NOVO JOGO\n")
    
    name = input("Digite o nome do seu herói: ").strip()
    if not name:
        name = "Aventureiro"
    
    # Seleção de classe
    print(f"\n{'='*50}")
    print("🎭 ESCOLHA SUA CLASSE")
    print(f"{'='*50}")
    print("\n1 - ⚔️  Guerreiro")
    print("   • +30% de dano corpo a corpo")
    print("   • Mais HP e Força")
    print("   • -20% de dano mágico")
    print("\n2 - 🔮 Mago")
    print("   • +50% de dano mágico")
    print("   • +30 Mana máxima (80 total)")
    print("   • Começa com magia Raio Elétrico")
    print("   • -30% de dano corpo a corpo")
    
    while True:
        class_choice = input("\nEscolha sua classe (1 ou 2): ").strip()
        
        if class_choice == "1":
            player_class = "guerreiro"
            print("\n⚔️  Você escolheu ser um Guerreiro!")
            break
        elif class_choice == "2":
            player_class = "mago"
            print("\n🔮 Você escolheu ser um Mago!")
            break
        else:
            print("❌ Opção inválida! Digite 1 ou 2.")
    
    player = Player(name, player_class)
    world = World()
    
    print(f"\n✨ Bem-vindo, {player.name} o {player_class.capitalize()}!")
    print("Você entra em uma dungeon antiga, esquecida pelo tempo...")
    
    input("\n[Pressione Enter para começar]")
    
    return player, world


def load_game_menu(save_mgr):
    """Menu para carregar jogo"""
    saves = save_mgr.list_saves()
    
    if not saves:
        print("\n❌ Nenhum save encontrado!")
        input("[Pressione Enter para continuar]")
        return None
    
    show_title()
    print("\n📂 CARREGAR JOGO\n")
    
    for i, save in enumerate(saves, 1):
        print(f"{i}. {save['player']} - Nível {save['level']}")
        print(f"   {save['timestamp']}")
        print()
    
    print("0 - Voltar")
    
    try:
        choice = int(input("\nEscolha um save: "))
        
        if choice == 0:
            return None
        
        if 1 <= choice <= len(saves):
            filename = saves[choice - 1]['filename']
            player, world = save_mgr.load_game(filename)
            
            if player and world:
                input("\n[Pressione Enter para continuar]")
                return player, world
    
    except ValueError:
        pass
    
    print("\n❌ Opção inválida!")
    input("[Pressione Enter para continuar]")
    return None


def show_room(world, player):
    """Exibe informações da sala atual"""
    print(world.get_room_description(player.position))
    
    directions = world.get_available_directions(player.position)
    if directions:
        print(f"🚪 Saídas: {', '.join(directions)}")


def show_actions():
    """Exibe ações disponíveis"""
    print("\n📋 AÇÕES:")
    print("1 - Mover")
    print("2 - Ver Status")
    print("3 - Ver Inventário")
    print("4 - Usar Item")
    print("5 - Equipar/Desequipar")
    print("6 - 🗺️  Ver Mapa")
    print("7 - Salvar Jogo")
    print("8 - Sair do Jogo")


def handle_movement(world, player):
    """Gerencia movimentação do player"""
    directions = world.get_available_directions(player.position)
    
    if not directions:
        print("\n❌ Não há saídas disponíveis!")
        return
    
    print(f"\n🚪 Direções: {', '.join(directions)}")
    direction = input("Para onde ir? ").strip().lower()
    
    new_room = world.move(player.position, direction)
    
    if new_room:
        player.position = new_room
        print(f"\n➡️  Você se move para {direction}...")
        input("[Pressione Enter]")
        return True
    else:
        print(f"\n❌ Não é possível ir para {direction}.")
        print("Há uma parede bloqueando o caminho!")
        input("[Pressione Enter]")
        return False


def handle_equipment(player):
    """Gerencia equipamentos"""
    print("\n⚔️  EQUIPAMENTOS\n")
    print("1 - Equipar Arma")
    print("2 - Equipar Escudo")
    print("3 - Equipar Armadura")
    print("4 - Desequipar Arma")
    print("5 - Desequipar Escudo")
    print("6 - Desequipar Armadura")
    print("0 - Voltar")
    
    choice = input("\nEscolha: ").strip()
    
    if choice == "1":
        # Equipar arma
        weapons = [item for item in player.inventory if item.item_type == "weapon"]
        if not weapons:
            print("\n❌ Você não tem armas!")
            return
        
        print("\n🗡️  Armas disponíveis:")
        for i, weapon in enumerate(weapons, 1):
            print(f"{i}. {weapon.name} (+{weapon.attack_bonus} Ataque)")
        
        try:
            idx = int(input("\nEscolha uma arma: ")) - 1
            if 0 <= idx < len(weapons):
                player.equip_weapon(weapons[idx])
        except ValueError:
            print("❌ Opção inválida!")
    
    elif choice == "2":
        # Equipar escudo
        shields = [item for item in player.inventory if item.item_type == "shield"]
        if not shields:
            print("\n❌ Você não tem escudos!")
            return
        
        print("\n🛡️  Escudos disponíveis:")
        for i, shield in enumerate(shields, 1):
            print(f"{i}. {shield.name} (+{shield.defense_bonus} Defesa)")
        
        try:
            idx = int(input("\nEscolha um escudo: ")) - 1
            if 0 <= idx < len(shields):
                player.equip_shield(shields[idx])
        except ValueError:
            print("❌ Opção inválida!")
    
    elif choice == "3":
        # Equipar armadura
        armors = [item for item in player.inventory if item.item_type == "armor"]
        if not armors:
            print("\n❌ Você não tem armaduras!")
            return
        
        print("\n🛡️  Armaduras disponíveis:")
        for i, armor in enumerate(armors, 1):
            print(f"{i}. {armor.name} (+{armor.defense_bonus} Defesa)")
        
        try:
            idx = int(input("\nEscolha uma armadura: ")) - 1
            if 0 <= idx < len(armors):
                player.equip_armor(armors[idx])
        except ValueError:
            print("❌ Opção inválida!")
    
    elif choice == "4":
        player.unequip_weapon()
    
    elif choice == "5":
        player.unequip_shield()
    
    elif choice == "6":
        player.unequip_armor()


def game_loop(player, world):
    """Loop principal do jogo"""
    save_mgr = SaveManager()
    game_running = True
    
    while game_running and player.is_alive():
        clear_screen()
        show_title()
        
        # Mostra sala atual
        show_room(world, player)
        
        # Processa eventos da sala
        result = world.process_room_events(player)
        
        # Verifica eventos especiais
        if result["event"] == "exit":
            show_victory(player)
            return
        
        elif result["event"] == "locked_exit":
            # Porta trancada, continua o jogo
            input("\n[Pressione Enter]")
            continue
        
        elif result["event"] == "combat" and result["result"] == "defeat":
            show_game_over()
            return
        
        # Mostra ações
        show_actions()
        
        choice = input("\n➤ ").strip()
        
        if choice == "1":
            # Mover
            handle_movement(world, player)
        
        elif choice == "2":
            # Status
            player.show_status()
            input("\n[Pressione Enter]")
        
        elif choice == "3":
            # Inventário
            player.show_inventory()
            input("\n[Pressione Enter]")
        
        elif choice == "4":
            # Usar item
            if not player.inventory:
                print("\n❌ Inventário vazio!")
            else:
                player.show_inventory()
                try:
                    idx = int(input("\nUsar qual item? (0 para cancelar): ")) - 1
                    if idx >= 0:
                        player.use_item(idx)
                except ValueError:
                    print("❌ Opção inválida!")
            
            input("\n[Pressione Enter]")
        
        elif choice == "5":
            # Equipamentos
            handle_equipment(player)
            input("\n[Pressione Enter]")
        
        elif choice == "6":
            # Ver Mapa
            minimap = MiniMap(world)
            minimap.show(player.position)
            input("\n[Pressione Enter]")
        
        elif choice == "7":
            # Salvar
            filename = input("\nNome do save (ou Enter para automático): ").strip()
            if not filename:
                filename = None
            elif not filename.endswith('.json'):
                filename += '.json'
            
            save_mgr.save_game(player, world, filename)
            input("\n[Pressione Enter]")
        
        elif choice == "8":
            # Sair
            print("\n❓ Deseja salvar antes de sair? (s/n): ", end="")
            if input().strip().lower() == 's':
                save_mgr.save_game(player, world)
            
            print("\n👋 Até logo!")
            game_running = False
        
        else:
            print("\n❌ Opção inválida!")
            input("[Pressione Enter]")


def show_victory(player):
    """Exibe tela de vitória"""
    clear_screen()
    print("\n" + "="*60)
    print("           🎉 VITÓRIA! 🎉")
    print("="*60)
    print(f"\nParabéns, {player.name}!")
    print("Você escapou da Dungeon of the Forgotten!")
    print(f"\nNível final: {player.level}")
    print(f"HP: {player.hp}/{player.max_hp}")
    print("\n" + "="*60)


def show_game_over():
    """Exibe tela de game over"""
    clear_screen()
    print("\n" + "="*60)
    print("           💀 GAME OVER 💀")
    print("="*60)
    print("\nVocê foi derrotado nas profundezas da dungeon...")
    print("Mas não desista! Tente novamente!")
    print("\n" + "="*60)


def main():
    """Função principal"""
    try:
        while True:
            result = main_menu()
            
            if result:
                player, world = result
                game_loop(player, world)
                
                # Após o jogo terminar
                input("\n[Pressione Enter para voltar ao menu]")
    
    except KeyboardInterrupt:
        print("\n\n👋 Jogo interrompido!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()