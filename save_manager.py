import json
import os
import copy
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
            "player_class": player.player_class,
            "level": player.level,
            "xp": player.xp,
            "max_hp": player.max_hp,
            "hp": player.hp,
            "mana": player.mana,
            "max_mana": player.max_mana,
            "bonus_mana": getattr(player, "bonus_mana", 0),
            "strength": player.strength,
            "vitality": player.vitality,
            "agility": player.agility,
            "skill_points": getattr(player, "skill_points", 0),
            "attribute_points": getattr(player, "attribute_points", 0),
            "unlocked_skills": list(getattr(player, "unlocked_skills", [])),
            "known_spells": [spell.name for spell in getattr(player, "known_spells", [])],
            "max_pa": getattr(player, "max_pa", 6),
            "position": player.position,
            "inventory": [item.name for item in player.inventory],
            "companions": copy.deepcopy(getattr(player, "companions", [])),
            "equipped_weapon": player.equipped_weapon.name if player.equipped_weapon else None,
            "equipped_shield": player.equipped_shield.name if player.equipped_shield else None,
            "equipped_armor": player.equipped_armor.name if player.equipped_armor else None,
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

            item_registry = self._get_item_registry()
            
            # Reconstrói o player
            from player import Player
            
            player_data = save_data["player"]
            player = Player(player_data["name"], player_data.get("player_class", "guerreiro"))
            player.inventory = []
            player.companions = []
            player.equipped_weapon = None
            player.equipped_shield = None
            player.equipped_armor = None
            player.known_spells = []
            
            # Restaura atributos
            player.level = player_data["level"]
            player.xp = player_data["xp"]
            player.max_hp = player_data["max_hp"]
            player.hp = player_data["hp"]
            player.mana = player_data.get("mana", player.mana)
            player.max_mana = player_data.get("max_mana", player.max_mana)
            player.bonus_mana = player_data.get("bonus_mana", 0)
            player.strength = player_data["strength"]
            player.vitality = player_data["vitality"]
            player.agility = player_data["agility"]
            player.skill_points = player_data.get("skill_points", 0)
            player.attribute_points = player_data.get("attribute_points", 0)
            player.unlocked_skills = list(player_data.get("unlocked_skills", []))
            player.max_pa = player_data.get("max_pa", getattr(player, "max_pa", 6))
            player.position = player_data["position"]
            from companions import hydrate_companion
            player.companions = [
                hydrate_companion(companion, player.level)
                for companion in player_data.get("companions", [])
                if companion
            ]
            
            # Recalcula stats (em caso de mudança no cálculo)
            player.base_attack = player.calculate_attack()
            player.base_defense = player.calculate_defense()
            
            # Restaura inventário
            for item_name in player_data.get("inventory", []):
                item = item_registry.get(item_name)
                if item:
                    player.inventory.append(copy.deepcopy(item))
            
            # Restaura equipamentos
            equipped_weapon_name = player_data.get("equipped_weapon")
            if equipped_weapon_name and equipped_weapon_name in item_registry:
                player.equipped_weapon = copy.deepcopy(item_registry[equipped_weapon_name])

            equipped_shield_name = player_data.get("equipped_shield")
            if equipped_shield_name and equipped_shield_name in item_registry:
                player.equipped_shield = copy.deepcopy(item_registry[equipped_shield_name])

            equipped_armor_name = player_data.get("equipped_armor")
            if equipped_armor_name and equipped_armor_name in item_registry:
                player.equipped_armor = copy.deepcopy(item_registry[equipped_armor_name])

            for spell_name in player_data.get("known_spells", []):
                spell = item_registry.get(spell_name)
                if spell:
                    player.known_spells.append(copy.deepcopy(spell))

            player.max_mana = player.calculate_max_mana()
            player.mana = min(player_data.get("mana", player.max_mana), player.max_mana)
            
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

    def _get_item_registry(self):
        """Cria um registro nome -> item base para reconstrução de saves."""
        import items as items_module
        from items import Item

        registry = {}
        for value in vars(items_module).values():
            if isinstance(value, Item):
                registry[value.name] = value

        return registry