class World:
    """Gerencia o mapa da dungeon como um grafo de salas"""
    
    def __init__(self):
        self.rooms = self.load_map()
        self.visited_rooms = set()  # Salas já visitadas
        self.defeated_enemies = set()  # IDs de salas com inimigos derrotados
        self.looted_rooms = set()  # Salas que já tiveram tesouro coletado
    
    def load_map(self):
        """Carrega o mapa da dungeon"""
        return {
            "1": {
                "name": "Sala Inicial",
                "type": "start",
                "description": "Uma sala fria e escura, iluminada por tochas antigas.\nO ar cheira a mofo e pedra molhada.",
                "connections": {"sul": "2"},
                "enemy": None,
                "item": None
            },
            "2": {
                "name": "Corredor de Pedra",
                "type": "corridor",
                "description": "Um corredor estreito com paredes rachadas.\nVocê escuta algo se movendo à distância.",
                "connections": {"norte": "1", "leste": "3", "sul": "4"},
                "enemy": None,
                "item": None
            },
            "3": {
                "name": "Sala do Goblin",
                "type": "enemy",
                "description": "Uma sala mal iluminada com manchas de sangue nas paredes.",
                "connections": {"oeste": "2"},
                "enemy": "goblin",
                "item": "rusty_sword"  # Drop do inimigo
            },
            "4": {
                "name": "Câmara do Tesouro",
                "type": "treasure",
                "description": "Você encontra um baú antigo coberto de poeira.",
                "connections": {"norte": "2", "leste": "5"},
                "enemy": None,
                "item": "health_potion"
            },
            "5": {
                "name": "Salão do Chefe",
                "type": "boss",
                "description": "Um salão enorme com teto alto.\nUm orc gigantesco bloqueia a passagem para a saída.",
                "connections": {"oeste": "4", "leste": "6"},
                "enemy": "orc_chief",
                "item": None
            },
            "6": {
                "name": "Saída",
                "type": "exit",
                "description": "Um feixe de luz natural entra pela passagem à frente.\nVocê sente o ar fresco pela primeira vez desde que entrou.",
                "connections": {},
                "enemy": None,
                "item": None
            }
        }
    
    def get_room(self, room_id):
        """Retorna os dados de uma sala"""
        return self.rooms.get(room_id)
    
    def get_room_description(self, room_id):
        """Retorna a descrição formatada de uma sala"""
        room = self.get_room(room_id)
        if not room:
            return "Sala desconhecida."
        
        # Marca sala como visitada
        self.visited_rooms.add(room_id)
        
        description = f"\n{'='*40}\n"
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
        if not room or not room.get("item"):
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
        item_name = room.get("item")
        
        self.looted_rooms.add(room_id)
        return item_name
    
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
