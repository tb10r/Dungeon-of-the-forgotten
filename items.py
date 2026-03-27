class Item:
    
    def __init__(self, name, item_type, description):
        self.name = name
        self.item_type = item_type  # "weapon", "shield", "consumable"
        self.description = description


class Weapon(Item):
    """Armas que aumentam ataque"""
    
    def __init__(self, name, attack_bonus, description, elemental_bonus=0, elemental_type=None, is_magical=False):
        super().__init__(name, "weapon", description)
        self.attack_bonus = attack_bonus
        self.elemental_bonus = elemental_bonus  # Bônus % para magias (50 = +50%)
        self.elemental_type = elemental_type  # "fire", "ice", "lightning", "arcane", "all"
        self.is_magical = is_magical  # Se True, attack_bonus não vale para físico


class Shield(Item):
    """Escudos que aumentam defesa"""
    
    def __init__(self, name, defense_bonus, description):
        super().__init__(name, "shield", description)
        self.defense_bonus = defense_bonus


class Armor(Item):
    """Armaduras que aumentam defesa e opcionalmente mana"""
    
    def __init__(self, name, defense_bonus, description, mana_bonus=0):
        super().__init__(name, "armor", description)
        self.defense_bonus = defense_bonus
        self.mana_bonus = mana_bonus  # Bônus de mana máxima


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


class Spell(Item):
    """Magias que podem ser aprendidas e usadas em combate"""
    
    def __init__(self, name, description, mana_cost, power, spell_type):
        super().__init__(name, "spell", description)
        self.mana_cost = mana_cost  # Custo em mana para lançar
        self.power = power  # Dano ou cura
        self.spell_type = spell_type  # "damage" ou "heal"

    def _get_spell_element(self):
        """Retorna o elemento principal da magia para bônus de arma."""
        name_lower = self.name.lower()

        if "fogo" in name_lower or "meteoro" in name_lower or "chama" in name_lower:
            return "fire"
        if "gelo" in name_lower or "ice" in name_lower:
            return "ice"
        if "raio" in name_lower or "elétrico" in name_lower or "relâmpago" in name_lower:
            return "lightning"
        if "arcan" in name_lower or "mágic" in name_lower or "maldição" in name_lower:
            return "arcane"

        return None
    
    def cast(self, caster, target=None):
        """Lança a magia"""
        if not caster.use_mana(self.mana_cost):
            print(f"\n❌ Mana insuficiente! Necessário: {self.mana_cost}, Disponível: {caster.mana}")
            return False
        
        print(f"\n✨ {caster.name} lançou {self.name}!")
        
        if self.spell_type == "damage":
            if target:
                # Aplica bônus de poder mágico da classe
                magic_power_bonus = getattr(caster, 'magic_power', 1.0)
                base_damage = int(self.power * magic_power_bonus)

                # Verifica bônus elemental da arma equipada
                weapon_bonus = 1.0
                if hasattr(caster, 'equipped_weapon') and caster.equipped_weapon:
                    weapon = caster.equipped_weapon
                    if weapon.elemental_bonus > 0:
                        spell_element = self._get_spell_element()
                        if weapon.elemental_type == "all" or weapon.elemental_type == spell_element:
                            weapon_bonus = 1.0 + (weapon.elemental_bonus / 100.0)
                            print(f"⚡ Bônus da {weapon.name}: +{weapon.elemental_bonus}%!")

                base_damage = int(base_damage * weapon_bonus)
                
                # Calcula dano considerando defesa mágica (50% da defesa normal)
                magic_defense = target.defense // 2
                damage = max(1, base_damage - magic_defense)
                target.take_damage(damage)
                print(f"💥 {target.name} recebeu {damage} de dano mágico!")
                print(f"🩸 {target.name} HP: {target.hp}/{target.max_hp}")
                return True
        
        elif self.spell_type == "heal":
            # Aplica bônus de poder mágico da classe também na cura
            magic_power_bonus = getattr(caster, 'magic_power', 1.0)
            heal_amount = int(self.power * magic_power_bonus)

            if hasattr(caster, 'equipped_weapon') and caster.equipped_weapon:
                weapon = caster.equipped_weapon
                spell_element = self._get_spell_element()
                if weapon.elemental_bonus > 0 and (weapon.elemental_type == "all" or weapon.elemental_type == spell_element):
                    heal_amount = int(heal_amount * (1.0 + (weapon.elemental_bonus / 100.0)))
                    print(f"⚡ Bônus da {weapon.name}: +{weapon.elemental_bonus}%!")
            
            old_hp = caster.hp
            caster.heal(heal_amount)
            healed = caster.hp - old_hp
            print(f"💚 Você curou {healed} HP! (HP: {caster.hp}/{caster.max_hp})")
            return True

        return False
        
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
    description="Uma runa negra pulsante com símbolos místicos. Emite uma energia sombria parece chamar para o altar sombrio.",
    summon_entity="blackwarrior"
)

necromancer_rune = Rune(
    name="Runa Necromântica",
    description="Uma runa sombria pulsando com energia profana. Use na Cripta para invocar algo terrível.",
    summon_entity="necromancer"
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

necromancer_robe = Armor(
    name="Manto do Necromante",
    defense_bonus=6,
    description="Manto negro impregnado com energia arcana sombria. Aumenta defesa e poder mágico.",
    mana_bonus=30
)

# Equipamento inicial para classes
warrior_sword = Weapon(
    name="Espada de Ferro do Guerreiro",
    attack_bonus=4,
    description="Uma espada sólida de ferro forjado, equilibrada para combate corpo a corpo."
)

warrior_armor = Armor(
    name="Couro Reforçado do Guerreiro",
    defense_bonus=4,
    description="Armadura de couro reforçada com placas de metal, oferece boa proteção sem comprometer mobilidade."
)

mage_staff = Weapon(
    name="Cajado Arcano do Aprendiz",
    attack_bonus=4,
    description="Um cajado de madeira imbuído com energia mágica, amplifica o poder dos feitiços."
)

mage_robe = Armor(
    name="Manto do Aprendiz",
    defense_bonus=2,
    description="Manto leve imbuído com encantamentos de proteção básica e amplificação mágica.",
    mana_bonus=20
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

# Magias
fireball = Spell(
    name="Bola de Fogo",
    description="Uma esfera flamejante que causa dano devastador ao inimigo.",
    mana_cost=15,
    power=25,
    spell_type="damage"
)

lightning_bolt = Spell(
    name="Raio Elétrico",
    description="Um raio fulminante que atinge o inimigo com precisão.",
    mana_cost=10,
    power=18,
    spell_type="damage"
)

ice_shard = Spell(
    name="Fragmento de Gelo",
    description="Cristais de gelo afiados que perfuram o inimigo.",
    mana_cost=12,
    power=20,
    spell_type="damage"
)

magical_heal = Spell(
    name="Cura Mágica",
    description="Uma luz curativa que restaura seus pontos de vida.",
    mana_cost=20,
    power=40,
    spell_type="heal"
)

meteor = Spell(
    name="Meteoro",
    description="Invoca um meteoro devastador do céu. A magia mais poderosa conhecida.",
    mana_cost=30,
    power=50,
    spell_type="damage"
)

necromancer_curser = Spell(
    name="Maldição do Necromante",
    description="Uma maldição sombria que drena a vida do inimigo.",
    mana_cost=25,
    power=70,
    spell_type="damage"
)

battle_axe = Weapon(
    name="Machado de Batalha",
    attack_bonus=6,
    description="Um machado pesado que causa grande dano."
)

flaming_sword = Weapon(
    name="Espada Flamejante",
    attack_bonus=7,
    description="Uma espada envolta em chamas eternas."
)

war_hammer = Weapon(
    name="Martelo de Guerra",
    attack_bonus=8,
    description="Martelo massivo forjado para destruir inimigos."
)

dragon_lance = Weapon(
    name="Lança do Dragão",
    attack_bonus=9,
    description="Lança lendária imbuída com poder dracônico."
)

# === ARMAS MÁGICAS DO MAGO ===
crystal_orb = Weapon(
    name="Orbe Cristalino",
    attack_bonus=1,
    description="Orbe que amplifica todas as magias.",
    elemental_bonus=25,
    elemental_type="all",
    is_magical=True
)

ice_wand = Weapon(
    name="Varinha de Gelo",
    attack_bonus=1,
    description="Varinha gélida que potencializa magias de gelo.",
    elemental_bonus=50,
    elemental_type="ice",
    is_magical=True
)

ancient_staff = Weapon(
    name="Cajado Ancião",
    attack_bonus=2,
    description="Cajado poderoso que amplifica todas as magias.",
    elemental_bonus=35,
    elemental_type="all",
    is_magical=True
)

shadow_grimoire = Weapon(
    name="Grimório das Sombras",
    attack_bonus=1,
    description="Livro de magia negra de poder imenso.",
    elemental_bonus=40,
    elemental_type="all",
    is_magical=True
)

fire_staff = Weapon(
    name="Cajado Flamejante",
    attack_bonus=1,
    description="Cajado que intensifica magias de fogo.",
    elemental_bonus=50,
    elemental_type="fire",
    is_magical=True
)

arcane_staff = Weapon(
    name="Bastão de Raios",
    attack_bonus=1,
    description="Bastão arcano que amplifica técnicas arcanas e elétricas.",
    elemental_bonus=50,
    elemental_type="arcane",
    is_magical=True
)

lightning_rod = arcane_staff