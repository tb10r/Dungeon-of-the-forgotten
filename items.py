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


class Armor(Item):
    """Armaduras que aumentam defesa"""
    
    def __init__(self, name, defense_bonus, description):
        super().__init__(name, "armor", description)
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


class Key(Item):
    """Chave especial necessária para sair da dungeon"""
    
    def __init__(self, name, description):
        super().__init__(name, "key", description)


class Rune(Item):
    """Runa mágica que pode invocar entidades no altar"""
    
    def __init__(self, name, description, summon_entity):
        super().__init__(name, "rune", description)
        self.summon_entity = summon_entity  # Nome do inimigo que invoca


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

exit_key = Key(
    name="Chave da Saída",
    description="Uma chave antiga e ornamentada. Parece ser importante para escapar daqui."
)

summoning_rune = Rune(
    name="Runa de Invocação",
    description="Uma runa negra pulsante com símbolos místicos. Emite uma energia sombria.",
    summon_entity="blackwarrior"
)

butcher_spatula = Weapon(
    name="espátula do Butcher",
    attack_bonus=4,
    description="Uma espátula grande e afiada, usada pelo Mestre Butcher em suas batalhas e criações culinárias."
)

iron_shield = Shield(
    name= "Escudo de Ferro",
    defense_bonus=4,
    description="Um escudo robusto feito de ferro forjado, oferecendo excelente proteção."
)

leather_armor = Armor(
    name="Armadura de Couro",
    defense_bonus=3,
    description="Uma armadura leve feita de couro curtido."
)

iron_armor = Armor(
    name="Armadura de Ferro",
    defense_bonus=5,
    description="Uma armadura pesada que oferece excelente proteção."
)

Blackwarrior_sword = Weapon(
    name="Blackwarrior's Blade",
    attack_bonus=10,
    description="A lâmina sombria empunhada pelo Blackwarrior, imbuída com energia mística."
)

Blackwarrior_armor = Armor(
    name="Blackwarrior's Armor",
    defense_bonus=10,
    description="A armadura negra usada pelo Blackwarrior, oferecendo proteção superior."
)