class Enemy:

    
    def __init__(self, name, hp, attack, defense, xp_reward, description):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.xp_reward = xp_reward
        self.description = description
    
    def take_damage(self, amount):

        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
    
    def is_alive(self):
        return self.hp > 0
    
    def get_attack_damage(self):
        return self.attack


class Goblin(Enemy):
    
    def __init__(self):
        super().__init__(
            name="Goblin",
            hp=50,          # ← 30 → 50 (mais resistente)
            attack=10,      # ← 6 → 10 (mais forte)
            defense=2,      # ← 2 → 4 (mais difícil de acertar)
            xp_reward=120,
            description="Um goblin pequeno, mas rápido, segura uma lâmina enferrujada."
        )
        self.can_flee = True


class OrcChief(Enemy):
    
    def __init__(self):
        super().__init__(
            name="Orc Chief",
            hp=90,
            attack=20,
            defense=7,
            xp_reward=180,
            description="Um orc enorme bloqueia a passagem, com cicatrizes de batalhas antigas."
        )
        self.can_flee = False
        self.turn_counter = 0
    
    def get_attack_damage(self):
        self.turn_counter += 1
        
        if self.turn_counter % 3 == 0:
            print(f"\n⚠️  {self.name} usa ATAQUE PODEROSO!")
            return self.attack * 2
        
        return self.attack


class MestreButcher(Enemy):
    """Chefe de cozinha esqueleto que ataca invasores"""
    
    def __init__(self):
        super().__init__(
            name="Mestre Butcher",
            hp=80,
            attack=14,
            defense=5,
            xp_reward=150,
            description="Um chefe de cozinha incrível que agora é só um esqueleto, porém ele ataca quem entra na cozinha dele."
        )
        self.can_flee = True


class Spaghettus(Enemy):
    """Macarrão vivo criado pelo Mestre Butcher"""
    
    def __init__(self):
        super().__init__(
            name="Spaghettus",
            hp=45,
            attack=8,
            defense=2,
            xp_reward=89,
            description="Um macarrão que ganhou vida graças ao Mestre Butcher."
        )
        self.can_flee = True


class Blackwarrior(Enemy):
    """Guerreiro sombrio invocável no Altar"""
    
    def __init__(self):
        super().__init__(
            name="Blackwarrior",
            hp=100,
            attack=18,
            defense=8,
            xp_reward=250,
            description="Um guerreiro sombrio que protege os segredos do altar."
        )
        self.can_flee = False