import random
from enemy import Goblin, OrcChief, MestreButcher, Blackwarrior, Spaghettus, esqueleto, Necromancer, PrisionGuard,Shadowmage, Dragonwarrior

class World:
    """Gerencia o mapa da dungeon como um grafo de salas"""
    
    def __init__(self):
        self.rooms = self.load_map()
        self.visited_rooms = set()  # Salas já visitadas
        self.defeated_enemies = set()  # IDs de salas com inimigos derrotados
        self.looted_rooms = set()  # Salas que já tiveram tesouro coletado
        self.previous_room = None
        self.randomize_treasure_loot()  # Gera loot aleatório para baús

    def load_map(self):
        """Carrega o mapa da dungeon"""
        return {
            "1": {
                "name": "Sala Inicial",
                "type": "start",
                "description": "Uma sala fria e escura, iluminada por tochas antigas.\nO ar cheira a mofo e pedra molhada.",
                "connections": {"sul": "2"},
                "enemy": None,
                "items": []
            },
            "2": {
                "name": "Corredor de Pedra",
                "type": "corridor",
                "description": "Um corredor estreito com paredes rachadas.\nVocê escuta algo se movendo à distância.",
                "connections": {"norte": "1", "leste": "3", "sul": "4", "oeste": "7"},
                "enemy": None,
                "items": []
            },
            "3": {
                "name": "Sala do Goblin",
                "type": "enemy",
                "description": "Uma sala mal iluminada com manchas de sangue nas paredes.",
                "connections": {"oeste": "2"},
                "enemy": "goblin",
                "items": ["rusty_sword"]  # Drop do inimigo
            },
            "4": {
                "name": "Câmara do Tesouro",
                "type": "treasure",
                "description": "Você encontra um baú antigo coberto de poeira.",
                "connections": {"norte": "2", "leste": "5"},
                "enemy": None,
                "items": []  # Será preenchido aleatoriamente
            },
            "5": {
                "name": "Salão do Chefe",
                "type": "boss",
                "description": "Um salão enorme com teto alto.\nUm orc gigantesco bloqueia a passagem para a saída.",
                "connections": {"oeste": "4", "leste": "6"},
                "enemy": "orc_chief",
                "items": ["exit_key"]
            },
            "6": {
                "name": "Saída",
                "type": "exit",
                "description": "Um feixe de luz natural entra pela passagem à frente.\nVocê sente o ar fresco pela primeira vez desde que entrou.",
                "connections": {"oeste": "5"},
                "enemy": None,
                "items": []
            },
            "7": {
                "name": "Arsenal Abandonado",
                "type": "treasure",
                "description": "Prateleiras enferrujadas exibem armas antigas quebradas.\nUm baú de ferro repousa no canto, ainda intacto.",
                "connections": {"leste": "2", "sul": "9",},
                "enemy": None,
                "items": []
            },
            "8": {
                "name": "Cozinha Abandonada",
                "type": "enemy",
                "description": "Uma cozinha em ruínas com manchas escuras nas tábuas de corte.\nIngredientes não identificáveis apodrecem sobre a mesa.",
                "connections": {"sul": "9"},
                "enemy": "mestre_butcher",
                "items": ["butcher_spatula"]
            },
            "9": {
                "name": "corredor ate a cozinha",
                "type": "enemy",
                "description": "Corredor mal iluminado com rastros de gordura nas paredes.\nFumaça fina e cinzenta emerge de uma passagem mais adiante.",
                "connections": {"norte": "8", "oeste": "7", "sul": "11"},
                "enemy": "spaghettus",
                "items": []
            },
            "10": {
                "name": "Biblioteca Esquecida",
                "type": "treasure",
                "description": "Prateleiras altas repletas de livros empoeirados e ilegíveis.\nTeias de aranha cobrem cada canto.",
                "connections": { "leste": "11"},
                "enemy": None,
                "items": []
            },
            "11": {
                "name": "Poço das Sombras",
                "type": "corridor",
                "description": "Um poço profundo domina o centro da sala.\nVocê escuta ecos distantes vindo de baixo.",
                "connections": {"norte": "9", "oeste": "10", "sul": "12"},
                "enemy": None,
                "items": []
            },
            "12": {
                "name": "Jardim Petrificado",
                "type": "treasure",
                "description": "Estátuas de pedra que um dia foram plantas cercam um baú ornamentado.\nA atmosfera é estranhamente pacífica.",
                "connections": {"norte": "11", "leste": "13"},
                "enemy": None,
                "items": []
            },
            "13": {
                "name": "Salão de Cristais",
                "type": "corridor",
                "description": "Cristais brilhantes crescem das paredes, emitindo uma luz azulada fraca.\nO som dos seus passos ecoa estranhamente.",
                "connections": {"oeste": "12", "norte": "14", "leste": "15"},
                "enemy": None,
                "items": []
            },
            "14": {
                "name": "Altar Sombrio",
                "type": "enemy",
                "description": "Um altar de pedra negra ocupa o centro da sala.\nMarcas de rituais antigos cobrem o chão.",
                "connections": {"sul": "13"},
                "enemy": "Blackwarrior",
                "items": ["Blackwarrior_sword", "Blackwarrior_armor"]
            },
            "15": {
                "name": "Câmara das Ruínas",
                "type": "treasure",
                "description": "Colunas quebradas e destroços de uma civilização antiga.\nUm baú de bronze está meio enterrado nos escombros.",
                "connections": {"oeste": "13", "sul": "16"},
                "enemy": None,
                "items": []
            },
            "16": {
                "name": "Passagem Estreita",
                "type": "corridor",
                "description": "Uma passagem tão estreita que você precisa andar de lado.\nO ar está abafado e quente.",
                "connections": {"norte": "15", "sul": "17", "oeste": "18"},
                "enemy": None,
                "items": []
            },
            "17": {
                "name": "Caverna de Estalactites",
                "type": "enemy",
                "description": "Estalactites afiadas pendem do teto como lanças.\nGotas de água ecoam pela caverna.",
                "connections": {"norte": "16"},
                "enemy": "goblin",
                "items": []
            },
            "18": {
                "name": "Depósito Inundado",
                "type": "treasure",
                "description": "Água até os tornozelos cobre o chão desta sala.\nCaixas empilhadas e um baú flutuam na água.",
                "connections": {"leste": "16", "sul": "19"},
                "enemy": None,
                "items": []
            },
            "19": {
                "name": "Catacumbas Antigas",
                "type": "enemy",
                "description": "Nichos nas paredes contêm ossos antigos.\nUm esqueleto reanimado patrulha entre as tumbas.",
                "connections": {"norte": "18", "leste": "20", "sul": "22"},
                "enemy": "esqueleto",
                "items": []
            },
            "20": {
                "name": "Cripta Profanada",
                "type": "boss",
                "description": "Sarcófagos quebrados e saqueados cercam um círculo necromântico.\nO ar é pesado com energia sombria.",
                "connections": {"oeste": "19", "sul": "21"},
                "enemy": "Necromancer",
                "items": ["necromancer_robe", "necromancer_curser"]
            },
            "21": {
                "name": "Câmara do Escriba",
                "type": "treasure",
                "description": "Uma escrivaninha antiga com pergaminhos deteriorados.\nUm pequeno baú está trancado sob a mesa.",
                "connections": {"norte": "20"},
                "enemy": None,
                "items": []
            },
            "22": {
                "name": "Túnel Desabado",
                "type": "enemy",
                "description": "Rochas e entulho bloqueiam parte da passagem.\nUm esqueleto emerge dos escombros.",
                "connections": {"norte": "19", "leste": "23"},
                "enemy": "esqueleto",
                "items": []
            },
            "23": {
                "name": "Sala das Armadilhas",
                "type": "enemy",
                "description": "Marcas de flechas nas paredes e buracos no chão.\nUm goblin patrulha os mecanismos enferrujados.",
                "connections": {"oeste": "22", "sul": "24"},
                "enemy": "goblin",
                "items": []
            },
            "24": {
                "name": "Torre em Ruínas",
                "type": "enemy",
                "description": "O que restou de uma torre interna.\nUm esqueleto guardando as escadas quebradas.",
                "connections": {"norte": "23", "leste": "25", "sul": "26"},
                "enemy": "esqueleto",
                "items": []
            },
            "25": {
                "name": "Observatório Destruído",
                "type": "treasure",
                "description": "Instrumentos astronômicos antigos cobertos de ferrugem.\nUm baú celestial jaz no centro.",
                "connections": {"oeste": "24"},
                "enemy": None,
                "items": []
            },
            "26": {
                "name": "Ponte de Pedra",
                "type": "enemy",
                "description": "Uma ponte sobre um abismo escuro.\nUm esqueleto bloqueia a passagem.",
                "connections": {"norte": "24", "sul": "27"},
                "enemy": "esqueleto",
                "items": []
            },
            "27": {
                "name": "Forja Apagada",
                "type": "enemy",
                "description": "Uma forja antiga ainda emite calor das brasas.\nFerramentas de ferreiro estão espalhadas.",
                "connections": {"norte": "26", "leste": "28"},
                "enemy": "goblin",
                "items": []
            },
            "28": {
                "name": "Arsenal Secreto",
                "type": "treasure",
                "description": "Uma sala escondida cheia de armas antigas.\nUm baú reforçado está encostado na parede.",
                "connections": {"oeste": "27", "sul": "29"},
                "enemy": None,
                "items": []
            },
            "29": {
                "name": "Salão dos Espelhos",
                "type": "enemy",
                "description": "Espelhos rachados refletem sua imagem distorcida.\nUm guarda se move entre os reflexos.",
                "connections": {"norte": "28", "oeste": "30"},
                "enemy": "PrisionGuard",
                "items": []
            },
            "30": {
                "name": "Prisão Abandonada",
                "type": "treasure",
                "description": "Celas enferrujadas com correntes penduradas.\nUm baú do carcereiro está em um canto.",
                "connections": {"leste": "29", "sul": "31"},
                "enemy": None,
                "items": []
            },
        

            "31": {
                "name": "Câmara dos Duelistas",
                "type": "multi_enemy",
                "description": "Dois guerreiros mortos-vivos empunham suas armas em posição de combate.\nSuas armaduras enferrujadas brilham fracamente à luz das tochas.",
                "connections": {"norte": "30",},  # Ajuste as conexões conforme seu mapa
                "enemies": ["Dragonwarrior", "Shadowmage"],  # Ou outro inimigo que preferir
                "items": ["dragon_lance", "shadow_grimoire"]  # Machado de Batalha + Espada Flamejante
            },
        }
    def randomize_treasure_loot(self):
        """Distribui itens aleatoriamente nos baús de tesouro sem repetição"""
        unique_loot_pool = [
            "simple_shield",
            "iron_shield",
            "leather_armor",
            "iron_armor",
            "fireball",
            "ice_shard",
            "magical_heal",
            "battle_axe",
            "flaming_sword",
            "crystal_orb",
            "ice_wand",
            "ancient_staff",
            "fire_staff",
            "lightning_rod",
        ]
                
        # Meteoro tem 33% de chance de aparecer
        if random.random() < 0.33:
            unique_loot_pool.append("meteor")
        
        # Identifica salas de tipo "treasure" (baús)
        treasure_rooms = [room_id for room_id, room in self.rooms.items() 
                         if room.get("type") == "treasure"]
        
        # Escolhe baús aleatórios para chave, runa do blackwarrior e runa do necromante
        if len(treasure_rooms) >= 3:
            key_room = random.choice(treasure_rooms)
            # Escolhe um baú diferente para a runa do blackwarrior
            remaining_rooms = [r for r in treasure_rooms if r != key_room]
            rune_room = random.choice(remaining_rooms)
            # Escolhe um baú diferente para a runa do necromante
            remaining_rooms = [r for r in remaining_rooms if r != rune_room]
            necro_rune_room = random.choice(remaining_rooms)
        else:
            key_room = rune_room = necro_rune_room = None
        
        # Distribui itens para cada baú (com reposição para não esvaziar os últimos baús)
        available_unique_items = unique_loot_pool[:]
        for room_id in treasure_rooms:
            room_items = []
            items_per_chest = random.randint(2, 3)
            unique_count = min(len(available_unique_items), items_per_chest)

            if unique_count > 0:
                selected_unique_items = random.sample(available_unique_items, unique_count)
                room_items.extend(selected_unique_items)
                for item_name in selected_unique_items:
                    available_unique_items.remove(item_name)

            while len(room_items) < items_per_chest:
                room_items.append("health_potion")
            
            # Adiciona a chave no baú escolhido
            if room_id == key_room:
                room_items.append("exit_key")
            
            # Adiciona a runa do blackwarrior no baú escolhido
            if room_id == rune_room:
                room_items.append("summoning_rune")
            
            # Adiciona a runa do necromante no baú escolhido
            if room_id == necro_rune_room:
                room_items.append("necromancer_rune")
            
            # Atribui itens ao baú
            self.rooms[room_id]["items"] = room_items
            
            # Debug: descomentar para ver a distribuição
            # print(f"Baú na sala {room_id} ({self.rooms[room_id]['name']}): {room_items}")
    
    def get_room(self, room_id):
        """Retorna os dados de uma sala"""
        return self.rooms.get(room_id)
    
    def get_room_description(self, room_id):
        """Retorna a descrição formatada de uma sala"""
        room = self.get_room(room_id)
        if not room:
            return "Sala desconhecida."
        
        # Verifica se já visitou antes
        is_revisit = room_id in self.visited_rooms
        
        # Marca sala como visitada
        self.visited_rooms.add(room_id)
        
        description = f"\n{'='*40}\n"
        
        # Se está revisitando, adiciona mensagem
        if is_revisit:
            description += f"Você volta para: {room['name']}\n"
        else:
            description += f"{room['name']}\n"
        
        description += f"{'='*40}\n"
        description += f"{room['description']}\n"
        
        return description
    
    def get_connections(self, room_id):
        """Retorna as direções disponíveis de uma sala"""
        room = self.get_room(room_id)
        if room:
            return room.get("connections", {})
        return {}
    
    def get_available_directions(self, room_id):
        """Retorna lista de direções disponíveis formatadas"""
        connections = self.get_connections(room_id)
        if not connections:
            return []
        return list(connections.keys())
    
    def move(self, current_room_id, direction):
        """Move o jogador para uma nova sala"""
        connections = self.get_connections(current_room_id)
        
        if direction.lower() not in connections:
            return None  # Direção inválida
        
        return connections[direction.lower()]
    
    def has_enemy(self, room_id):
        """Verifica se a sala tem um inimigo vivo"""
        room = self.get_room(room_id)
        if not room:
            return False

        has_single_enemy = bool(room.get("enemy"))
        has_multi_enemy = bool(room.get("enemies"))
        if not has_single_enemy and not has_multi_enemy:
            return False
        
        # Verifica se o inimigo já foi derrotado
        return room_id not in self.defeated_enemies
    
    def get_enemy_type(self, room_id):
        """Retorna o tipo de inimigo na sala"""
        room = self.get_room(room_id)
        if room and self.has_enemy(room_id):
            return room.get("enemy")
        return None
    
    def defeat_enemy(self, room_id):
        """Marca inimigo da sala como derrotado"""
        self.defeated_enemies.add(room_id)
        print(f"\n✅ O inimigo desta sala foi derrotado!")
    
    def has_treasure(self, room_id):
        """Verifica se a sala tem tesouro não coletado"""
        room = self.get_room(room_id)
        if not room or not room.get("items"):
            return False
        
        # Salas com inimigos só dão loot após derrotar o inimigo
        if (room.get("enemy") or room.get("enemies")) and room_id not in self.defeated_enemies:
            return False
        
        # Verifica se o tesouro já foi coletado
        return room_id not in self.looted_rooms
    
    def get_treasure(self, room_id):
        """Retorna o item do tesouro e marca como coletado"""
        if not self.has_treasure(room_id):
            return None
        
        room = self.get_room(room_id)
        item_names = room.get("items", [])
        
        self.looted_rooms.add(room_id)
        return item_names
    
    def is_exit(self, room_id):
        """Verifica se a sala é a saída"""
        room = self.get_room(room_id)
        return room and room.get("type") == "exit"
    
    def show_map_status(self):
        """Exibe status do mapa (para debug)"""
        print(f"\n📊 Status do Mapa:")
        print(f"Salas visitadas: {len(self.visited_rooms)}/6")
        print(f"Inimigos derrotados: {len(self.defeated_enemies)}")
        print(f"Tesouros coletados: {len(self.looted_rooms)}")

    def create_enemy(self, room_id):
        """Cria instância de inimigo baseado no tipo da sala"""
        
        enemy_type = self.get_enemy_type(room_id)
        if isinstance(enemy_type, str):
            enemy_type = enemy_type.lower()
        
        if enemy_type == "goblin":
            return Goblin()
        elif enemy_type == "orc_chief":
            return OrcChief()
        elif enemy_type == "mestre_butcher":
            return MestreButcher()
        elif enemy_type == "spaghettus":
            return Spaghettus()
        elif enemy_type == "blackwarrior":
            return Blackwarrior()
        elif enemy_type == "esqueleto":
            return esqueleto()
        elif enemy_type == "necromancer":
            return Necromancer()
        elif enemy_type == "prision_guard":
            return PrisionGuard()
        elif enemy_type == "shadowmage":
            return Shadowmage()
        elif enemy_type == "dragonwarrior":
            return Dragonwarrior()
        
        return None
    
    def create_enemy_by_name(self, enemy_name):
        """Cria instância de inimigo baseado no nome"""
        if isinstance(enemy_name, str):
            enemy_name = enemy_name.lower()

        if enemy_name == "goblin":
            return Goblin()
        elif enemy_name == "orc_chief":
            return OrcChief()
        elif enemy_name == "mestre_butcher":
            return MestreButcher()
        elif enemy_name == "spaghettus":
            return Spaghettus()
        elif enemy_name == "blackwarrior":
            return Blackwarrior()
        elif enemy_name == "esqueleto":
            return esqueleto()
        elif enemy_name == "necromancer":
            return Necromancer()
        elif enemy_name == "prision_guard":
            return PrisionGuard()
        elif enemy_name == "shadowmage":
            return Shadowmage()
        elif enemy_name == "dragonwarrior":
            return Dragonwarrior()
        
        return None
    
    def get_item_from_room(self, room_id, player_class=None, source="any"):
        """Retorna instâncias dos itens da sala.
        source:
          - "chest": aplica filtro por classe + neutros e remove spells
                    - "boss": aplica filtro por classe e mantém spells/recompensas especiais
          - "any": mantém comportamento antigo (sem filtro)
        """
        from items import (
            rusty_sword, simple_shield, health_potion, exit_key, summoning_rune, necromancer_rune,
            iron_shield, leather_armor, iron_armor, necromancer_robe, Blackwarrior_sword, Blackwarrior_armor,
            butcher_spatula, fireball, lightning_bolt, ice_shard, magical_heal, meteor, necromancer_curser,
            battle_axe, flaming_sword, war_hammer, dragon_lance, crystal_orb, ice_wand, ancient_staff,
            shadow_grimoire, fire_staff, lightning_rod
        )

        item_names = self.get_treasure(room_id)
        if not item_names:
            return []

        # Mapeia nome do item para instância
        items_map = {
            "rusty_sword": rusty_sword,
            "simple_shield": simple_shield,
            "health_potion": health_potion,
            "summoning_rune": summoning_rune,
            "necromancer_rune": necromancer_rune,
            "iron_shield": iron_shield,
            "leather_armor": leather_armor,
            "iron_armor": iron_armor,
            "necromancer_robe": necromancer_robe,
            "Blackwarrior_sword": Blackwarrior_sword,
            "Blackwarrior_armor": Blackwarrior_armor,
            "butcher_spatula": butcher_spatula,
            "fireball": fireball,
            "lightning_bolt": lightning_bolt,
            "ice_shard": ice_shard,
            "magical_heal": magical_heal,
            "meteor": meteor,
            "necromancer_curser": necromancer_curser,
            "battle_axe": battle_axe,
            "flaming_sword": flaming_sword,
            "war_hammer": war_hammer,
            "dragon_lance": dragon_lance,
            "exit_key": exit_key,
            "crystal_orb": crystal_orb,
            "ice_wand": ice_wand,
            "ancient_staff": ancient_staff,
            "shadow_grimoire": shadow_grimoire,
            "fire_staff": fire_staff,
            "lightning_rod": lightning_rod,
        }

        neutral_items = {
            "health_potion",
            "simple_shield", "iron_shield", "rusty_sword"
        }
        warrior_items = {
            "battle_axe", "flaming_sword", "war_hammer", "dragon_lance",
            "leather_armor", "iron_armor", "Blackwarrior_sword",
            "Blackwarrior_armor", "butcher_spatula", "summoning_rune"
        }
        mage_items = {
            "crystal_orb", "ice_wand", "ancient_staff", "shadow_grimoire",
            "fire_staff", "lightning_rod", "necromancer_robe", "necromancer_rune",
            "necromancer_curser"
        }

        allowed_names = set(items_map.keys())
        if source == "chest":
            allowed_names = set(neutral_items)
            if player_class == "guerreiro":
                allowed_names |= warrior_items
            elif player_class == "mago":
                allowed_names |= mage_items
        elif source == "boss":
            if player_class == "guerreiro":
                allowed_names = set(warrior_items)
            elif player_class == "mago":
                allowed_names = set(mage_items)

        items = []
        for item_name in item_names:
            item = items_map.get(item_name)
            if not item:
                continue

            if source in {"chest", "boss"}:
                if item_name not in allowed_names:
                    continue
                if source == "chest" and item.item_type == "spell":
                    continue

            items.append(item)

        # Garantia: baú nunca vazio após filtro de classe
        if source == "chest" and not items:
            fallback_item = items_map.get("health_potion")
            if fallback_item:
                items.append(fallback_item)

        return items

    def process_room_events(self, player):
        """Processa eventos da sala atual (combate, tesouros, etc)"""
        from combat_pa import CombatPA
        
        room_id = player.position
        room = self.get_room(room_id)
        
        if not room:
            return {"event": "none"}
        
        # Marca sala como visitada
        self.visited_rooms.add(room_id)
        
        # Verifica se é a Cripta Profanada (sala 20) e se o jogador tem a runa necromântica
        if room_id == "20" and room_id not in self.defeated_enemies:
            # Verifica se tem a runa necromântica
            necro_rune = next((item for item in player.inventory 
                              if item.item_type == "rune" and item.summon_entity == "necromancer"), None)
            
            if necro_rune:
                print(f"\n🔮 O círculo necromântico no chão reage à {necro_rune.name}!")
                print("💀 Energia profana começa a surgir dos sarcófagos...")
                
                choice = input("\n⚰️  Usar a runa para invocar o necromante? (s/n): ").strip().lower()
                
                if choice == 's':
                    # Remove a runa do inventário
                    player.remove_from_inventory(necro_rune)
                    print(f"\n🌀 Você coloca a {necro_rune.name} no centro do círculo!")
                    print("💀 Ossos começam a se erguer e se fundir!")
                    print("👻 O NECROMANTE FOI INVOCADO!")
                    
                    # Cria o necromante e inicia combate
                    from enemy import Necromancer
                    enemy = Necromancer()
                    print(f"\n{enemy.description}")
                    
                    from combat_pa import CombatPA
                    combat = CombatPA(player, enemy)
                    result = combat.run_combat()
                    
                    if result["result"] == "victory":
                        self.defeat_enemy(room_id)
                        
                        # Adiciona loot do necromante (manto + magia poderosa)
                        items = self.get_item_from_room(room_id)
                        if items:
                            print(f"\n💎 Você encontrou {len(items)} item(ns) do necromante derrotado!")
                            
                            for item in items:
                                # Se for magia, aprende diretamente
                                if item.item_type == "spell":
                                    player.learn_spell(item)
                                    print(f"  ✨ {item.name} - Magia aprendida!")
                                else:
                                    player.add_to_inventory(item)
                                    print(f"  ✓ {item.name}")
                                
                                # Pergunta se quer equipar armadura
                                if item.item_type == "armor":
                                    equip = input(f"\n🛡️  Equipar {item.name}? (s/n): ").strip().lower()
                                    if equip == 's':
                                        player.equip_armor(item)
                        
                        return {
                            "event": "combat",
                            "result": "victory",
                            "enemy": enemy.name
                        }
                    elif result["result"] == "defeat":
                        return {
                            "event": "combat",
                            "result": "defeat"
                        }
                    elif result["result"] == "fled":
                        return {
                            "event": "combat",
                            "result": "fled"
                        }
                else:
                    print("\n🚶 Você decide não invocar o necromante agora...")
                    return {"event": "none"}
            else:
                print("\n💀 O círculo necromântico está inerte. Talvez você precise de algo especial para ativá-lo...")
                return {"event": "none"}
        
        # Verifica se é o Altar Sombrio (sala 14) e se o jogador tem a runa
        if room_id == "14" and room_id not in self.defeated_enemies:
            # Verifica se tem a runa de invocação
            rune = next((item for item in player.inventory if item.item_type == "rune"), None)
            
            if rune:
                print(f"\n🔮 O altar pulsa com energia ao detectar a {rune.name} em sua posse!")
                print("⚡ Símbolos místicos começam a brilhar na pedra negra...")
                
                choice = input("\n💀 Usar a runa para invocar o guardião sombrio? (s/n): ").strip().lower()
                
                if choice == 's':
                    # Remove a runa do inventário
                    player.remove_from_inventory(rune)
                    print(f"\n🌀 Você coloca a {rune.name} sobre o altar!")
                    print("⚡ Uma explosão de energia sombria enche a sala!")
                    print("👹 O BLACKWARRIOR FOI INVOCADO!")
                    
                    # Cria o Blackwarrior e inicia combate
                    enemy = Blackwarrior()
                    print(f"\n{enemy.description}")
                    
                    combat = CombatPA(player, enemy)
                    result = combat.run_combat()
                    
                    if result["result"] == "victory":
                        self.defeat_enemy(room_id)
                        return {
                            "event": "combat",
                            "result": "victory",
                            "enemy": enemy.name
                        }
                    elif result["result"] == "defeat":
                        return {
                            "event": "combat",
                            "result": "defeat"
                        }
                    elif result["result"] == "fled":
                        return {
                            "event": "combat",
                            "result": "fled"
                        }
                else:
                    print("\n🚪 Você decide não usar a runa... por enquanto.")
                    return {"event": "none"}
            else:
                print("\n⚫ O altar está vazio e inerte.")
                print("   Parece que algo especial poderia ativá-lo...")
                return {"event": "none"}
        
        # Verifica se é a saída
        if self.is_exit(room_id):
            # Verifica se o jogador tem a chave
            has_key = any(item.item_type == "key" for item in player.inventory)
            
            if has_key:
                return {"event": "exit"}
            else:
                print("\n🔒 A porta está trancada!")
                print("💡 Você precisa encontrar a Chave da Saída para escapar.")
                print("   Procure nos baús pela dungeon...")
                return {"event": "locked_exit"}
        
        # Verifica se há MÚLTIPLOS inimigos (novo sistema)
        room = self.get_room(room_id)
        if "enemies" in room and room["enemies"] and room_id not in self.defeated_enemies:
            print(f"\n⚔️  MÚLTIPLOS INIMIGOS APARECEM!")
            
            enemies_list = room["enemies"]
            all_defeated = True
            
            for i, enemy_name in enumerate(enemies_list, 1):
                enemy = self.create_enemy_by_name(enemy_name)
                
                if not enemy:
                    continue
                    
                print(f"\n{'='*60}")
                print(f"🗡️  COMBATE {i}/{len(enemies_list)}: {enemy.name}")
                print(f"{'='*60}")
                print(f"{enemy.description}")
                
                combat = CombatPA(player, enemy)
                result = combat.run_combat()
                
                if result["result"] == "defeat":
                    all_defeated = False
                    return {"event": "combat", "result": "defeat"}
                
                elif result["result"] == "fled":
                    return {"event": "combat", "result": "fled"}
                
                print(f"\n✅ {enemy.name} derrotado! ({i}/{len(enemies_list)})")
                
                # Cura pequena entre combates (exceto no último)
                if i < len(enemies_list):
                    heal = 15
                    player.heal(heal)
                    player.restore_mana(10)
                    print(f"💚 Você recupera {heal} HP e 10 mana entre combates!")
                    input("\n[Pressione Enter para o próximo combate]")
            
            if all_defeated:
                self.defeat_enemy(room_id)
                
                # Coleta drops de TODOS os inimigos
                items = self.get_item_from_room(room_id)
                if items:
                    print(f"\n💎 Você encontrou {len(items)} item(ns) dos inimigos derrotados!")
                    for item in items:
                        if item.item_type == "spell":
                            player.learn_spell(item)
                            print(f"  ✨ {item.name} - Magia aprendida!")
                        else:
                            player.add_to_inventory(item)
                            print(f"  ✓ {item.name}")
                        
                        # Pergunta se quer equipar
                        if item.item_type == "weapon":
                            equip = input(f"\n⚔️  Equipar {item.name}? (s/n): ").strip().lower()
                            if equip == 's':
                                player.equip_weapon(item)
                        elif item.item_type == "shield":
                            equip = input(f"\n🛡️  Equipar {item.name}? (s/n): ").strip().lower()
                            if equip == 's':
                                player.equip_shield(item)
                        elif item.item_type == "armor":
                            equip = input(f"\n🛡️  Equipar {item.name}? (s/n): ").strip().lower()
                            if equip == 's':
                                player.equip_armor(item)
                
                return {
                    "event": "combat",
                    "result": "victory",
                    "enemy": "múltiplos inimigos"
                }
        
        # Verifica se há inimigo
        if self.has_enemy(room_id):
            enemy = self.create_enemy(room_id)
            
            if enemy:
                print(f"\n⚠️  Um {enemy.name} aparece!")
                print(f"{enemy.description}")
                
                # Pergunta se quer batalhar
                print("\n⚔️  O que fazer?")
                print("1 - Batalhar")
                print("2 - Recuar para sala anterior")
                
                choice = input("\nEscolha: ").strip()
                
                if choice == "2":
                    print(f"\n🏃 Você recua rapidamente antes que o {enemy.name} ataque!")
                    # Não marca sala como visitada para combate
                    return {
                        "event": "retreat",
                        "enemy": enemy.name
                    }
                
                # Inicia combate
                combat = CombatPA(player, enemy)
                result = combat.run_combat()
                
                if result["result"] == "victory":
                    # Marca inimigo como derrotado
                    self.defeat_enemy(room_id)
                # Verifica se há loot
                if self.has_treasure(room_id):
                    items = self.get_item_from_room(room_id)  # ← MUDOU: pega lista
                    if items:
                        print(f"\n💎 Você encontrou {len(items)} item(ns)!")
                        
                        for item in items:  # ← MUDOU: loop sobre todos os itens
                            # Se for magia, aprende diretamente
                            if item.item_type == "spell":
                                player.learn_spell(item)
                                print(f"  ✨ {item.name} - Magia aprendida!")
                            else:
                                player.add_to_inventory(item)
                                print(f"  ✓ {item.name}")
                            
                            # Pergunta se quer equipar (se for arma ou escudo)
                            if item.item_type == "weapon":
                                equip = input(f"\n⚔️  Equipar {item.name}? (s/n): ").strip().lower()
                                if equip == 's':
                                    player.equip_weapon(item)
                            
                            elif item.item_type == "shield":
                                equip = input(f"\n🛡️  Equipar {item.name}? (s/n): ").strip().lower()
                                if equip == 's':
                                    player.equip_shield(item)
                            
                            elif item.item_type == "armor":
                                equip = input(f"\n🛡️  Equipar {item.name}? (s/n): ").strip().lower()
                                if equip == 's':
                                    player.equip_armor(item)   
                    # Verifica se há loot
                if self.has_treasure(room_id):
                    item = self.get_item_from_room(room_id)
                    if item:
                        player.add_to_inventory(item)
                        print(f"\n💎 {item.name} encontrado(a)!")
                        
                        # Pergunta se quer equipar (se for arma ou escudo)
                        if item.item_type == "weapon":
                            equip = input(f"\n⚔️  Equipar {item.name}? (s/n): ").strip().lower()
                            if equip == 's':
                                player.equip_weapon(item)
                        
                        elif item.item_type == "shield":
                            equip = input(f"\n🛡️  Equipar {item.name}? (s/n): ").strip().lower()
                            if equip == 's':
                                player.equip_shield(item)
                    
                    return {
                        "event": "combat",
                        "result": "victory",
                        "enemy": enemy.name
                    }
                
                elif result["result"] == "defeat":
                    return {
                        "event": "combat",
                        "result": "defeat"
                    }
                
                elif result["result"] == "fled":
                    return {
                        "event": "combat",
                        "result": "fled"
                    }
        
        # Verifica se há tesouro (sem inimigo)
        elif self.has_treasure(room_id):
            items = self.get_item_from_room(room_id, player.player_class, source="chest")
            if items:
                print(f"\n💎 Você encontrou {len(items)} item(ns)!")
                
                for item in items:  # ← MUDOU: loop sobre todos os itens
                    # Se for magia, aprende diretamente
                    if item.item_type == "spell":
                        player.learn_spell(item)
                        print(f"  ✨ {item.name} - Magia aprendida!")
                        print(f"     {item.description}")
                    else:
                        player.add_to_inventory(item)
                        print(f"  ✓ {item.name} - {item.description}")
                    
                    # Pergunta se quer equipar (se for arma ou escudo)
                    if item.item_type == "weapon":
                        equip = input(f"\n⚔️  Equipar {item.name}? (s/n): ").strip().lower()
                        if equip == 's':
                            player.equip_weapon(item)
                    
                    elif item.item_type == "shield":
                        equip = input(f"\n🛡️  Equipar {item.name}? (s/n): ").strip().lower()
                        if equip == 's':
                            player.equip_shield(item)
                    
                    elif item.item_type == "armor":
                        equip = input(f"\n🛡️  Equipar {item.name}? (s/n): ").strip().lower()
                        if equip == 's':
                            player.equip_armor(item)
                
                return {
                    "event": "treasure",
                    "items": [item.name for item in items]  # ← MUDOU: lista de nomes
                }
        
        return {"event": "none"}
