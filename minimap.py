class MiniMap:
    """Sistema de minimapa com fog of war"""
    
    def __init__(self, world):
        self.world = world
        # Define posições das salas no grid do mapa (linha, coluna)
        self.room_positions = {
            # Área inicial (canto superior esquerdo)
            "1": (0, 4),
            "2": (2, 4),
            "3": (2, 8),
            "4": (4, 4),
            "5": (4, 8),
            "6": (4, 12),
            "7": (2, 0),
            
            # Área da cozinha (lado esquerdo)
            "8": (0, 0),
            "9": (4, 0),
            "10": (6, 0),
            "11": (6, 4),
            
            # Área central
            "12": (8, 4),
            "13": (8, 8),
            "14": (6, 8),
            "15": (8, 12),
            
            # Área direita (catacumbas/cripta)
            "16": (10, 12),
            "17": (12, 12),
            "18": (10, 8),
            "19": (12, 8),
            "20": (12, 10),
            "21": (14, 10),
            
            # Área inferior (túneis/torre)
            "22": (14, 8),
            "23": (14, 12),
            "24": (16, 12),
            "25": (16, 14),
            "26": (18, 12),
            "27": (20, 12),
            "28": (20, 14),
            "29": (22, 14),
            "30": (22, 12),
            "31": (24, 12),
        }
    
    def get_room_icon(self, room_id, player_pos):
        """Retorna o ícone apropriado para a sala"""
        room = self.world.get_room(room_id)
        
        # Jogador está aqui
        if room_id == player_pos:
            return "👤"
        
        # Sala não visitada (névoa)
        if room_id not in self.world.visited_rooms:
            return "  "
        
        # Saída
        if room.get("type") == "exit":
            return "🚪"
        
        # Boss
        if room.get("type") == "boss":
            if room_id in self.world.defeated_enemies:
                return "💀"
            else:
                return "👑"
        
        # Inimigo
        if room.get("enemy"):
            if room_id in self.world.defeated_enemies:
                return "💀"
            else:
                return "⚔️"
        
        # Tesouro
        if room.get("type") == "treasure":
            if room_id in self.world.looted_rooms:
                return "✓"
            else:
                return "💎"
        
        # Corredor/normal
        return "□"
    
    def draw_connection(self, from_pos, to_pos, visited_from, visited_to):
        """Desenha conexão entre salas se ambas foram visitadas"""
        if not (visited_from and visited_to):
            return None
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Horizontal
        if from_row == to_row:
            mid_col = (from_col + to_col) // 2
            return (from_row, mid_col, "━")
        
        # Vertical
        if from_col == to_col:
            mid_row = (from_row + to_row) // 2
            return (mid_row, from_col, "┃")
        
        return None
    
    def show(self, player_pos):
        """Exibe o minimapa com fog of war"""
        # Cria grid vazio
        max_row = max(pos[0] for pos in self.room_positions.values()) + 1
        max_col = max(pos[1] for pos in self.room_positions.values()) + 1
        
        grid = [[" " for _ in range(max_col)] for _ in range(max_row)]
        
        # Adiciona conexões entre salas visitadas
        for room_id, pos in self.room_positions.items():
            room = self.world.get_room(room_id)
            connections = room.get("connections", {})
            
            for direction, connected_id in connections.items():
                if connected_id in self.room_positions:
                    from_visited = room_id in self.world.visited_rooms
                    to_visited = connected_id in self.world.visited_rooms
                    
                    conn = self.draw_connection(
                        pos, 
                        self.room_positions[connected_id],
                        from_visited,
                        to_visited
                    )
                    
                    if conn:
                        row, col, char = conn
                        if 0 <= row < max_row and 0 <= col < max_col:
                            grid[row][col] = char
        
        # Adiciona ícones das salas
        for room_id, (row, col) in self.room_positions.items():
            icon = self.get_room_icon(room_id, player_pos)
            if icon != "  ":  # Não desenha salas não visitadas
                grid[row][col] = icon[0] if len(icon) == 1 else icon
        
        # Imprime o mapa
        print(f"\n{'='*60}")
        print(f"{'🗺️  MAPA DA DUNGEON':^60}")
        print(f"{'='*60}")
        
        for row in grid:
            print(" " + "".join(row))
        
        print(f"\n{'Legenda:':^60}")
        print(f"{'👤 = Você  |  ⚔️ = Inimigo  |  💀 = Derrotado':^60}")
        print(f"{'💎 = Tesouro  |  ✓ = Coletado  |  🚪 = Saída':^60}")
        print(f"{'👑 = Boss  |  □ = Corredor':^60}")
        print(f"{'='*60}\n")
