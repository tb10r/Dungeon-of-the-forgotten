class Item:
    
    def __init__(self, name, item_type, description):
        self.name = name
        self.item_type = item_type  # "weapon", "shield", "consumable"
        self.description = description


class Weapon(Item):
    """Armas que aumentam ataque"""
    
    def __init__(self, name, attack_bonus, description):
        super().__init__(name, "weapon", description)
        self.attack_bonus = attack_bonus


class Shield(Item):
    """Escudos que aumentam defesa"""
    
    def __init__(self, name, defense_bonus, description):
        super().__init__(name, "shield", description)
        self.defense_bonus = defense_bonus


class Potion(Item):
    """Poções consumíveis que curam HP"""
    
    def __init__(self, name, heal_amount, description):
        super().__init__(name, "consumable", description)
        self.heal_amount = heal_amount
    
    def use(self, player):
        """Usa a poção no jogador"""
        if player.hp >= player.max_hp:
            print(f"\n❌ Seu HP já está cheio!")
            return False
        
        old_hp = player.hp
        player.heal(self.heal_amount)
        healed = player.hp - old_hp
        
        print(f"\n✅ Você usou {self.name}!")
        print(f"💚 Curou {healed} HP (HP: {player.hp}/{player.max_hp})")
        return True


# Instâncias dos itens do jogo
rusty_sword = Weapon(
    name="Espada Enferrujada",
    attack_bonus=3,
    description="Uma espada velha, mas ainda afiada o suficiente."
)

simple_shield = Shield(
    name="Escudo Simples",
    defense_bonus=2,
    description="Um escudo de madeira reforçado com metal."
)

health_potion = Potion(
    name="Poção de Cura",
    heal_amount=30,
    description="Uma poção vermelha brilhante que restaura 30 HP."
)