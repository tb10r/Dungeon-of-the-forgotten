class Player:
    """Classe que representa o jogador"""
    
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.xp = 0
        
        # Atributos primários
        self.strength = 5      # Afeta ataque (1 força = +2 ataque)
        self.vitality = 5      # Afeta HP (1 vitalidade = +10 HP)
        self.agility = 5       # Afeta defesa (1 agilidade = +1 defesa)
        
        # Stats derivados dos atributos
        self.max_hp = self.calculate_max_hp()
        self.hp = self.max_hp
        self.base_attack = self.calculate_attack()
        self.base_defense = self.calculate_defense()
        
        self.inventory = []
        self.position = "1"
        self.equipped_weapon = None
        self.equipped_shield = None
    
    def calculate_max_hp(self):
        """Calcula HP máximo baseado em vitalidade"""
        return 30 + (self.vitality * 10)
    
    def calculate_attack(self):
        """Calcula ataque base baseado em força"""
        return 3 + (self.strength * 2)
    
    def calculate_defense(self):
        """Calcula defesa base baseada em agilidade"""
        return 1 + (self.agility * 1)
    
    def get_xp_needed(self):
        """Calcula XP necessário para próximo nível"""
        return self.level * 100
    
    def gain_xp(self, amount):
        """Ganha XP e verifica se subiu de nível"""
        self.xp += amount
        print(f"\n+{amount} XP")
        
        # Verifica se subiu de nível
        while self.xp >= self.get_xp_needed():
            self.level_up()
    
    def level_up(self):
        """Sobe de nível e permite distribuir pontos de atributo"""
        self.xp -= self.get_xp_needed()
        self.level += 1
        
        print(f"\n{'='*50}")
        print(f"✨ Você subiu para o nível {self.level}! ✨")
        print(f"{'='*50}")
        print("Você ganhou 3 pontos de atributo para distribuir!")
        
        # Distribuir pontos
        self.distribute_attribute_points(3)
        
        # Recalcula todas as stats baseado nos novos atributos
        old_max_hp = self.max_hp
        self.max_hp = self.calculate_max_hp()
        self.base_attack = self.calculate_attack()
        self.base_defense = self.calculate_defense()
        
        # Cura a diferença de HP ganho
        hp_gained = self.max_hp - old_max_hp
        self.hp += hp_gained
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        
        print(f"\n✅ HP restaurado! (+{hp_gained} HP)")
        self.show_status()
    
    def distribute_attribute_points(self, points):
        """Permite ao jogador distribuir pontos entre atributos"""
        remaining = points
        
        print("\n📊 Seus atributos atuais:")
        print(f"  Força: {self.strength} (Ataque: {self.calculate_attack()})")
        print(f"  Vitalidade: {self.vitality} (HP: {self.calculate_max_hp()})")
        print(f"  Agilidade: {self.agility} (Defesa: {self.calculate_defense()})")
        
        while remaining > 0:
            print(f"\n{'='*40}")
            print(f"Pontos restantes: {remaining}")
            print(f"{'='*40}")
            print("1 - Força → Aumenta Ataque em +2 por ponto")
            print("2 - Vitalidade → Aumenta HP em +10 por ponto")
            print("3 - Agilidade → Aumenta Defesa em +1 por ponto")
            print("4 - Ver stats atuais")
            print("5 - Distribuir automaticamente")
            
            try:
                choice = input("\nOnde investir? ").strip()
                
                if choice == '5' or choice.lower() == 'auto':
                    self.auto_distribute_attributes(remaining)
                    break
                
                choice = int(choice)
                
                if choice == 4:
                    print(f"\n📊 Preview das stats:")
                    print(f"  Força: {self.strength} → Ataque: {self.calculate_attack()}")
                    print(f"  Vitalidade: {self.vitality} → HP: {self.calculate_max_hp()}")
                    print(f"  Agilidade: {self.agility} → Defesa: {self.calculate_defense()}")
                    continue
                
                if choice not in [1, 2, 3]:
                    print("❌ Opção inválida! Escolha 1-5")
                    continue
                
                # Pergunta quantos pontos investir
                while True:
                    try:
                        amount = input(f"Quantos pontos investir? (1-{remaining}): ").strip()
                        amount = int(amount)
                        
                        if amount < 1:
                            print("❌ Deve investir pelo menos 1 ponto!")
                            continue
                        
                        if amount > remaining:
                            print(f"❌ Você só tem {remaining} pontos disponíveis!")
                            continue
                        
                        # Investe os pontos
                        if choice == 1:
                            self.strength += amount
                            remaining -= amount
                            new_attack = self.calculate_attack()
                            print(f"✅ Força aumentada em +{amount} (Total: {self.strength})!")
                            print(f"   Ataque será: {new_attack} (+{amount * 2})")
                        
                        elif choice == 2:
                            self.vitality += amount
                            remaining -= amount
                            new_hp = self.calculate_max_hp()
                            print(f"✅ Vitalidade aumentada em +{amount} (Total: {self.vitality})!")
                            print(f"   HP máximo será: {new_hp} (+{amount * 10})")
                        
                        elif choice == 3:
                            self.agility += amount
                            remaining -= amount
                            new_defense = self.calculate_defense()
                            print(f"✅ Agilidade aumentada em +{amount} (Total: {self.agility})!")
                            print(f"   Defesa será: {new_defense} (+{amount * 1})")
                        
                        break  # Sai do loop de quantidade
                    
                    except ValueError:
                        print("❌ Digite um número válido!")
            
            except ValueError:
                print("❌ Digite um número válido!")
        
            print(f"\n{'='*40}")
            print("✅ Todos os pontos foram distribuídos!")
            print(f"{'='*40}")
            
        def auto_distribute_attributes(self, points):
            """Distribui pontos automaticamente de forma balanceada"""
            # Estratégia: 1 Força, 1 Vitalidade, 1 Agilidade (balanceado)
            strength_points = points // 3
            vitality_points = points // 3
            agility_points = points - strength_points - vitality_points
            
            self.strength += strength_points
            self.vitality += vitality_points
            self.agility += agility_points
            
            print("\n🤖 Distribuição automática (balanceada):")
            print(f"  Força: +{strength_points} (Total: {self.strength})")
            print(f"  Vitalidade: +{vitality_points} (Total: {self.vitality})")
            print(f"  Agilidade: +{agility_points} (Total: {self.agility})")
    
    def take_damage(self, amount):
        """Recebe dano"""
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
    
    def heal(self, amount):
        """Cura HP (não ultrapassa máximo)"""
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    
    def is_alive(self):
        """Verifica se o jogador está vivo"""
        return self.hp > 0
    
    def add_to_inventory(self, item):
        """Adiciona item ao inventário"""
        self.inventory.append(item)
        print(f"\n{item.name} adicionado ao inventário!")
    
    def remove_from_inventory(self, item):
        """Remove item do inventário"""
        if item in self.inventory:
            self.inventory.remove(item)
    
    def show_inventory(self):
        """Exibe inventário formatado"""
        if not self.inventory:
            print("\n🎒 Inventário vazio!")
            return
        
        print(f"\n{'='*40}")
        print("🎒 INVENTÁRIO")
        print(f"{'='*40}")
        
        for i, item in enumerate(self.inventory, 1):
            icon = "⚔️" if item.item_type == "weapon" else "🛡️" if item.item_type == "shield" else "🧪"
            print(f"{i}. {icon} {item.name}")
            print(f"   {item.description}")
            
            if item.item_type == "weapon":
                print(f"   Bônus: +{item.attack_bonus} Ataque")
            elif item.item_type == "shield":
                print(f"   Bônus: +{item.defense_bonus} Defesa")
            elif item.item_type == "consumable":
                print(f"   Efeito: Cura {item.heal_amount} HP")
            print()
        
        print(f"{'='*40}")
    
    def use_item(self, item_index):
        """Usa um item consumível do inventário"""
        if item_index < 0 or item_index >= len(self.inventory):
            print("\n❌ Item não encontrado no inventário!")
            return False
        
        item = self.inventory[item_index]
        
        if item.item_type != "consumable":
            print(f"\n❌ {item.name} não pode ser usado! (Equipamentos devem ser equipados)")
            return False
        
        # Usa o item (chama o método use do item)
        if item.use(self):
            # Remove do inventário após uso
            self.remove_from_inventory(item)
            return True
        
        return False
    
    def get_total_attack(self):
        """Retorna ataque total (base + equipamentos)"""
        total = self.base_attack
        if self.equipped_weapon:
            total += self.equipped_weapon.attack_bonus
        return total
    
    def get_total_defense(self):
        """Retorna defesa total (base + equipamentos)"""
        total = self.base_defense
        if self.equipped_shield:
            total += self.equipped_shield.defense_bonus
        return total
    
    def equip_weapon(self, weapon):
        """Equipa uma arma (apenas uma por vez)"""
        if self.equipped_weapon:
            print(f"\n{self.equipped_weapon.name} foi desequipada.")
        
        self.equipped_weapon = weapon
        print(f"\n✅ {weapon.name} equipada!")
        print(f"Ataque agora: {self.get_total_attack()}")
    
    def equip_shield(self, shield):
        """Equipa um escudo"""
        if self.equipped_shield:
            print(f"\n{self.equipped_shield.name} foi desequipado.")
        
        self.equipped_shield = shield
        print(f"\n✅ {shield.name} equipado!")
        print(f"Defesa agora: {self.get_total_defense()}")
    
    def unequip_weapon(self):
        """Remove a arma equipada"""
        if self.equipped_weapon:
            weapon = self.equipped_weapon
            self.equipped_weapon = None
            print(f"\n{weapon.name} foi desequipada.")
            return weapon
        return None
    
    def unequip_shield(self):
        """Remove o escudo equipado"""
        if self.equipped_shield:
            shield = self.equipped_shield
            self.equipped_shield = None
            print(f"\n{shield.name} foi desequipado.")
            return shield
        return None
    
    def show_status(self):
        """Exibe status completo do jogador"""
        print(f"\n{'='*40}")
        print(f"👤 {self.name} - Nível {self.level}")
        print(f"{'='*40}")
        print(f"❤️  HP: {self.hp} / {self.max_hp}")
        print(f"⚔️  Ataque: {self.get_total_attack()} (Base: {self.base_attack})")
        print(f"🛡️  Defesa: {self.get_total_defense()} (Base: {self.base_defense})")
        print(f"✨ XP: {self.xp} / {self.get_xp_needed()}")
        print(f"\n📊 Atributos:")
        print(f"  💪 Força: {self.strength}")
        print(f"  ❤️  Vitalidade: {self.vitality}")
        print(f"  ⚡ Agilidade: {self.agility}")
        
        if self.equipped_weapon or self.equipped_shield:
            print(f"\n🎒 Equipamentos:")
            if self.equipped_weapon:
                print(f"  ⚔️  {self.equipped_weapon.name} (+{self.equipped_weapon.attack_bonus})")
            if self.equipped_shield:
                print(f"  🛡️  {self.equipped_shield.name} (+{self.equipped_shield.defense_bonus})")
        
        print(f"{'='*40}")