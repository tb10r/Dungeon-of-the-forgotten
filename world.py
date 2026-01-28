import random
from enemy import Goblin, OrcChief, MestreButcher, Blackwarrior, Spaghettus

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
                "items": []
            },
            "6": {
                "name": "Saída",
                "type": "exit",
                "description": "Um feixe de luz natural entra pela passagem à frente.\nVocê sente o ar fresco pela primeira vez desde que entrou.",
                "connections": {},
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
                "connections": {"norte": "8", "sul": "11"},
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
                "connections": {"oeste": "13"},
                "enemy": None,
                "items": []
            }
        }
    
    def randomize_treasure_loot(self):
        """Distribui itens aleatoriamente nos baús de tesouro sem repetição"""
        # Lista de todos os itens disponíveis para baús
        available_items = [
            "health_potion",
            "simple_shield",
            "iron_shield",
            "leather_armor",
            "iron_armor",
            # Adicione mais itens aqui conforme criar
        ]
        
        # Embaralha a lista para ordem aleatória
        random.shuffle(available_items)
        
        # Identifica salas de tipo "treasure" (baús)
        treasure_rooms = [room_id for room_id, room in self.rooms.items() 
                         if room.get("type") == "treasure"]
        
        # Escolhe baús aleatórios para chave e runa
        if treasure_rooms:
            key_room = random.choice(treasure_rooms)
            # Escolhe um baú diferente para a runa
            rune_room = random.choice([r for r in treasure_rooms if r != key_room])
        
        # Distribui itens únicos para cada baú
        item_index = 0
        for room_id in treasure_rooms:
            # Cada baú terá apenas 1 item
            room_items = []
            if item_index < len(available_items):
                room_items.append(available_items[item_index])
                item_index += 1
            
            # Adiciona a chave no baú escolhido
            if room_id == key_room:
                room_items.append("exit_key")
            
            # Adiciona a runa no baú escolhido
            if room_id == rune_room:
                room_items.append("summoning_rune")
            
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
        if not room or not room.get("enemy"):
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
        if room.get("enemy") and room_id not in self.defeated_enemies:
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
        
        return None
    
    def get_item_from_room(self, room_id):
        """Retorna instância do item da sala"""
        from items import rusty_sword, simple_shield, health_potion, exit_key, summoning_rune, iron_shield, leather_armor, iron_armor, Blackwarrior_sword, Blackwarrior_armor, butcher_spatula
        
        item_names = self.get_treasure(room_id)
        
        if not item_names:
            return []
        
        # Mapeia nome do item para instância
        items_map = {
            "rusty_sword": rusty_sword,
            "simple_shield": simple_shield,
            "health_potion": health_potion,
            "exit_key": exit_key,
            "summoning_rune": summoning_rune,
            "iron_shield": iron_shield,
            "leather_armor": leather_armor,
            "iron_armor": iron_armor,
            "Blackwarrior_sword": Blackwarrior_sword,
            "Blackwarrior_armor": Blackwarrior_armor,
            "butcher_spatula": butcher_spatula
        }
        
        items = []
        for item_name in item_names:
            item = items_map.get(item_name)
            if item:
                items.append(item)
        
        return items

    def process_room_events(self, player):
        """Processa eventos da sala atual (combate, tesouros, etc)"""
        from combat import Combat
        
        room_id = player.position
        room = self.get_room(room_id)
        
        if not room:
            return {"event": "none"}
        
        # Marca sala como visitada
        self.visited_rooms.add(room_id)
        
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
                    
                    combat = Combat(player, enemy)
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
                combat = Combat(player, enemy)
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
            items = self.get_item_from_room(room_id)  # ← MUDOU: pega lista
            if items:
                print(f"\n💎 Você encontrou {len(items)} item(ns)!")
                
                for item in items:  # ← MUDOU: loop sobre todos os itens
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
