import json
import os
from datetime import datetime

class SaveManager:
    """Gerencia slavar e carregar o jogo"""
    def __init__(self,save_dir="saves"):
        self.save_dir = save_dir

        # Cria a pasta de saves se não existir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    def save_game(self, player, world, filename=None):
        """Salva o estado do jogo em JSON"""
        if filename is None:
            #Gera nomee com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"save_{timestamp}.json"
        
        # Prepara dados do player
        player_data = {
            "name": player.name,
            "level": player.level,
            "xp": player.xp,
            "max_hp": player.max_hp,
            "hp": player.hp,
            "strength": player.strength,
            "vitality": player.vitality,
            "agility": player.agility,
            "position": player.position,
            "inventory": [
                {
                    "name": item.name,
                    "type": item.item_type,
                    "description": item.description,
                    "attack_bonus": getattr(item, 'attack_bonus', None),
                    "defense_bonus": getattr(item, 'defense_bonus', None),
                    "heal_amount": getattr(item, 'heal_amount', None)
                }
                for item in player.inventory
            ],
            "equipped_weapon": {
                "name": player.equipped_weapon.name,
                "attack_bonus": player.equipped_weapon.attack_bonus
            } if player.equipped_weapon else None,
            "equipped_shield": {
                "name": player.equipped_shield.name,
                "defense_bonus": player.equipped_shield.defense_bonus
            } if player.equipped_shield else None
        }
        
        # Prepara dados do world
        world_data = {
            "visited_rooms": list(world.visited_rooms),
            "defeated_enemies": list(world.defeated_enemies),
            "looted_rooms": list(world.looted_rooms)
        }
        
        # Combina tudo
        save_data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "player": player_data,
            "world": world_data
        }
        
        # Salva em arquivo
        filepath = os.path.join(self.save_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Jogo salvo em: {filename}")
            return filepath
        
        except Exception as e:
            print(f"\n❌ Erro ao salvar: {e}")
            return None
    
    def load_game(self, filename):
        """Carrega o estado do jogo do JSON"""
        filepath = os.path.join(self.save_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"\n❌ Arquivo não encontrado: {filename}")
            return None, None
        
        try:
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            # Reconstrói o player
            from player import Player
            from items import rusty_sword, simple_shield, health_potion, Potion, Weapon, Shield
            
            player_data = save_data["player"]
            player = Player(player_data["name"])
            
            # Restaura atributos
            player.level = player_data["level"]
            player.xp = player_data["xp"]
            player.max_hp = player_data["max_hp"]
            player.hp = player_data["hp"]
            player.strength = player_data["strength"]
            player.vitality = player_data["vitality"]
            player.agility = player_data["agility"]
            player.position = player_data["position"]
            
            # Recalcula stats (em caso de mudança no cálculo)
            player.base_attack = player.calculate_attack()
            player.base_defense = player.calculate_defense()
            
            # Restaura inventário
            for item_data in player_data["inventory"]:
                if item_data["type"] == "weapon":
                    item = Weapon(
                        item_data["name"],
                        item_data["attack_bonus"],
                        item_data["description"]
                    )
                elif item_data["type"] == "shield":
                    item = Shield(
                        item_data["name"],
                        item_data["defense_bonus"],
                        item_data["description"]
                    )
                elif item_data["type"] == "consumable":
                    item = Potion(
                        item_data["name"],
                        item_data["heal_amount"],
                        item_data["description"]
                    )
                else:
                    continue
                
                player.inventory.append(item)
            
            # Restaura equipamentos
            if player_data["equipped_weapon"]:
                for item in player.inventory:
                    if item.name == player_data["equipped_weapon"]["name"]:
                        player.equipped_weapon = item
                        break
            
            if player_data["equipped_shield"]:
                for item in player.inventory:
                    if item.name == player_data["equipped_shield"]["name"]:
                        player.equipped_shield = item
                        break
            
            # Reconstrói o world
            from world import World
            world = World()
            
            world_data = save_data["world"]
            world.visited_rooms = set(world_data["visited_rooms"])
            world.defeated_enemies = set(world_data["defeated_enemies"])
            world.looted_rooms = set(world_data["looted_rooms"])
            
            print(f"\n📂 Jogo carregado de: {filename}")
            return player, world
        
        except json.JSONDecodeError:
            print(f"\n❌ Arquivo corrompido: {filename}")
            return None, None
        
        except KeyError as e:
            print(f"\n❌ Dados inválidos no arquivo: {e}")
            return None, None
        
        except Exception as e:
            print(f"\n❌ Erro ao carregar: {e}")
            return None, None
    
    def list_saves(self):
        """Lista todos os saves disponíveis"""
        saves = []
        
        if not os.path.exists(self.save_dir):
            return saves
        
        for filename in os.listdir(self.save_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.save_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    saves.append({
                        "filename": filename,
                        "player": data["player"]["name"],
                        "level": data["player"]["level"],
                        "timestamp": data.get("timestamp", "Desconhecido")
                    })
                except:
                    pass
        
        return sorted(saves, key=lambda x: x["timestamp"], reverse=True)
    
    def save_exists(self, filename):
        """Verifica se um save existe"""
        filepath = os.path.join(self.save_dir, filename)
        return os.path.exists(filepath)
    
    def delete_save(self, filename):
        """Deleta um arquivo de save"""
        filepath = os.path.join(self.save_dir, filename)
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"\n🗑️  Save deletado: {filename}")
                return True
            except Exception as e:
                print(f"\n❌ Erro ao deletar: {e}")
                return False
        
        return False
    
    def show_save_list(self):
        """Exibe lista de saves de forma formatada"""
        saves = self.list_saves()
        
        if not saves:
            print("\n📂 Nenhum save encontrado!")
            return
        
        print(f"\n{'='*60}")
        print("📂 ARQUIVOS SALVOS")
        print(f"{'='*60}")
        
        for i, save in enumerate(saves, 1):
            print(f"\n{i}. {save['filename']}")
            print(f"   Jogador: {save['player']}")
            print(f"   Nível: {save['level']}")
            print(f"   Data: {save['timestamp']}")
        
        print(f"\n{'='*60}")            