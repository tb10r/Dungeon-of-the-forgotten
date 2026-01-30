class Player:
    """Classe que representa o jogador"""
    
    def __init__(self, name, player_class="guerreiro"):
        self.name = name
        self.player_class = player_class  # "guerreiro" ou "mago"
        self.level = 1
        self.xp = 0
        
        # Atributos primários (ajustados por classe)
        if player_class == "mago":
            self.strength = 3          # Menos força
            self.vitality = 4          # Menos vitalidade
            self.agility = 6           # Mais agilidade
            self.magic_power = 1.5     # 50% mais dano mágico
            self.melee_bonus = 0.7     # 30% menos dano corpo a corpo
        else:  # guerreiro
            self.strength = 4          # Mais força
            self.vitality = 6          # Mais vitalidade
            self.agility = 4           # Menos agilidade
            self.magic_power = 0.8     # 20% menos dano mágico
            self.melee_bonus = 1.3     # 30% mais dano corpo a corpo
        
        # Stats derivados dos atributos
        self.max_hp = self.calculate_max_hp()
        self.hp = self.max_hp
        self.base_attack = self.calculate_attack()
        self.base_defense = self.calculate_defense()
        
        # Sistema de mana para magias (ajustado por classe)
        if player_class == "mago":
            self.max_mana = 80  # Mago começa com mais mana
        else:
            self.max_mana = 50  # Guerreiro tem mana padrão
        
        self.mana = self.max_mana
        self.known_spells = []  # Lista de magias aprendidas
        
        # Mago começa com uma magia inicial
        if player_class == "mago":
            from items import lightning_bolt
            self.known_spells.append(lightning_bolt)
        
        self.inventory = []
        self.position = "1"
        self.equipped_weapon = None
        self.equipped_shield = None
        self.equipped_armor = None
        
        # Equipar itens iniciais baseado na classe (antes de calcular stats)
        self._equip_starting_gear()
        
        # Recalcula stats com equipamentos equipados
        self.max_mana = self.calculate_max_mana()
        self.mana = self.max_mana
    
    def _equip_starting_gear(self):
        """Equipa arma e armadura inicial baseado na classe escolhida"""
        import copy
        from items import health_potion, simple_shield
        
        if self.player_class == "mago":
            from items import mage_staff, mage_robe
            self.equipped_weapon = mage_staff
            self.equipped_armor = mage_robe
            # Mago começa com 2 poções no inventário (cópias independentes)
            self.inventory.append(copy.deepcopy(health_potion))
            self.inventory.append(copy.deepcopy(health_potion))
        else:  # guerreiro
            from items import warrior_sword, warrior_armor
            self.equipped_weapon = warrior_sword
            self.equipped_armor = warrior_armor
            # Guerreiro começa com 1 poção e 1 escudo simples no inventário
            self.inventory.append(copy.deepcopy(health_potion))
            self.inventory.append(copy.deepcopy(simple_shield))
    
    def calculate_max_hp(self):
        """Calcula HP máximo baseado em vitalidade"""
        return 30 + (self.vitality * 10)
    
    def calculate_attack(self):
        """Calcula ataque base baseado em força"""
        return 3 + (self.strength * 2)
    
    def calculate_defense(self):
        """Calcula defesa base baseada em agilidade"""
        return 1 + (self.agility * 1)
    
    def calculate_crit_chance(self):
        """Calcula chance de acerto crítico baseada em agilidade"""
        base_crit = 5  # 5% base
        agi_bonus = self.agility * 1  # +1% por ponto de agilidade
        return min(base_crit + agi_bonus, 50)  # Cap em 50%
    
    def calculate_max_mana(self):
        """Calcula mana máxima total incluindo bônus de equipamentos"""
        # Usa o max_mana da classe (já definido no __init__)
        base_mana = 80 if self.player_class == "mago" else 50
        armor_bonus = 0
        
        if self.equipped_armor and hasattr(self.equipped_armor, 'mana_bonus'):
            armor_bonus = self.equipped_armor.mana_bonus
        
        return base_mana + armor_bonus
    
    def roll_critical_hit(self):
        """Verifica se o ataque é crítico"""
        import random
        crit_chance = self.calculate_crit_chance()
        roll = random.random() * 100  # Número entre 0 e 100
        return roll < crit_chance
    
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
        
        #salva o hp maximo atual antes de distribuir os pontos
        old_max_hp = self.max_hp
        # Distribuir pontos
        self.distribute_attribute_points(3)
        
        # Recalcula todas as stats baseado nos novos atributos
        old_max_hp = self.max_hp
        self.max_hp = self.calculate_max_hp()
        self.base_attack = self.calculate_attack()
        self.base_defense = self.calculate_defense()
        
        self.hp = self.max_hp  # Restaura HP ao máximo ao subir de nível
        self.mana = self.max_mana  # Restaura mana ao máximo
        hp_gained = self.max_hp - old_max_hp
        
        print(f"\n✅ HP e Mana restaurados! (+{hp_gained} HP)")
        self.show_status()
    
    def distribute_attribute_points(self, points):
        """Permite ao jogador distribuir pontos entre atributos"""
        remaining = points
        
        print("\n📊 Seus atributos atuais:")
        print(f"  Força: {self.strength} (Ataque: {self.calculate_attack()})")
        print(f"  Vitalidade: {self.vitality} (HP: {self.calculate_max_hp()})")
        print(f"  Agilidade: {self.agility} (Defesa: {self.calculate_defense()})")
        print(f"  Mana Máxima: {self.max_mana}")
        
        while remaining > 0:
            print(f"\n{'='*40}")
            print(f"Pontos restantes: {remaining}")
            print(f"{'='*40}")
            print("1 - Força → Aumenta Ataque em +2 por ponto")
            print("2 - Vitalidade → Aumenta HP em +10 por ponto")
            print("3 - Agilidade → Aumenta Defesa em +1 e Taxa Crítico em +1% por ponto")
            print("4 - Mana → Aumenta Mana Máxima em +10 por ponto")
            print("5 - Ver stats atuais")
            
            try:
                choice = input("\nOnde investir? ").strip()
                
                if choice == '6' or choice.lower() == 'auto':
                    self.auto_distribute_attributes(remaining)
                    break
                
                choice = int(choice)
                
                if choice == 5:
                    print(f"\n📊 Preview das stats:")
                    print(f"  Força: {self.strength} → Ataque: {self.calculate_attack()}")
                    print(f"  Vitalidade: {self.vitality} → HP: {self.calculate_max_hp()}")
                    print(f"  Agilidade: {self.agility} → Defesa: {self.calculate_defense()} | Crítico: {self.calculate_crit_chance()}%")
                    print(f"  Mana Máxima: {self.max_mana}")
                    continue
                
                if choice not in [1, 2, 3, 4]:
                    print("❌ Opção inválida! Escolha 1-6")
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
                            new_crit = self.calculate_crit_chance()
                            print(f"✅ Agilidade aumentada em +{amount} (Total: {self.agility})!")
                            print(f"   Defesa será: {new_defense} (+{amount})")
                            print(f"   Taxa de Crítico será: {new_crit}% (+{amount}%)")
                        
                        elif choice == 4:
                            old_max_mana = self.max_mana
                            self.max_mana += (amount * 10)
                            remaining -= amount
                            print(f"✅ Mana Máxima aumentada em +{amount * 10} (Total: {self.max_mana})!")
                            print(f"   Mana: {old_max_mana} → {self.max_mana}")
                        
                        break  # Sai do loop de quantidade
                    
                    except ValueError:
                        print("❌ Digite um número válido!")
            
            except ValueError:
                print("❌ Digite um número válido!")
        
            print(f"\n{'='*40}")
            print("✅ Todos os pontos foram distribuídos!")
            print(f"{'='*40}")
    
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
    
    def restore_mana(self, amount):
        """Restaura mana (não ultrapassa máximo)"""
        self.mana += amount
        if self.mana > self.max_mana:
            self.mana = self.max_mana
    
    def use_mana(self, amount):
        """Usa mana. Retorna True se havia mana suficiente"""
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False
    
    def learn_spell(self, spell):
        """Aprende uma nova magia"""
        if spell not in self.known_spells:
            self.known_spells.append(spell)
            print(f"\n✨ Você aprendeu a magia: {spell.name}!")
            print(f"📖 {spell.description}")
            print(f"💙 Custo de mana: {spell.mana_cost}")
            return True
        else:
            print(f"\n⚠️  Você já conhece {spell.name}!")
            return False
    
    def show_spells(self):
        """Exibe lista de magias conhecidas"""
        if not self.known_spells:
            print("\n✨ Você ainda não conhece nenhuma magia!")
            return
        
        print(f"\n{'='*40}")
        print("✨ MAGIAS CONHECIDAS")
        print(f"{'='*40}")
        print(f"💙 Mana: {self.mana}/{self.max_mana}")
        print(f"{'='*40}")
        
        for i, spell in enumerate(self.known_spells, 1):
            print(f"{i}. 🔮 {spell.name} - {spell.mana_cost} mana")
            print(f"   {spell.description}")
            if spell.spell_type == "damage":
                print(f"   💥 Dano: {spell.power}")
            elif spell.spell_type == "heal":
                print(f"   💚 Cura: {spell.power} HP")
            print()
    
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
        """Retorna ataque total (base + equipamentos + bônus de classe)"""
        total = self.base_attack
        if self.equipped_weapon:
            total += self.equipped_weapon.attack_bonus
        # Aplica bônus/penalidade de classe para combate corpo a corpo
        total = int(total * self.melee_bonus)
        return total
    
    def get_total_defense(self):
        """Retorna defesa total (base + equipamentos)"""
        total = self.base_defense
        if self.equipped_shield:
            total += self.equipped_shield.defense_bonus
        if self.equipped_armor:
            total += self.equipped_armor.defense_bonus
        return total
    
    def equip_weapon(self, weapon):
        """Equipa uma arma (apenas uma por vez)"""
        import copy
        
        # Se já tem arma equipada, devolve ao inventário
        if self.equipped_weapon:
            self.inventory.append(copy.deepcopy(self.equipped_weapon))
            print(f"\n{self.equipped_weapon.name} foi desequipada e retornou ao inventário.")
        
        # Remove a nova arma do inventário se estiver lá
        if weapon in self.inventory:
            self.inventory.remove(weapon)
        
        self.equipped_weapon = weapon
        print(f"\n✅ {weapon.name} equipada!")
        print(f"Ataque agora: {self.get_total_attack()}")
    
    def equip_shield(self, shield):
        """Equipa um escudo"""
        import copy
        
        # Se já tem escudo equipado, devolve ao inventário
        if self.equipped_shield:
            self.inventory.append(copy.deepcopy(self.equipped_shield))
            print(f"\n{self.equipped_shield.name} foi desequipado e retornou ao inventário.")
        
        # Remove o novo escudo do inventário se estiver lá
        if shield in self.inventory:
            self.inventory.remove(shield)
        
        self.equipped_shield = shield
        print(f"\n✅ {shield.name} equipado!")
        print(f"Defesa agora: {self.get_total_defense()}")
    
    def equip_armor(self, armor):
        """Equipa uma armadura"""
        import copy
        old_max_mana = self.max_mana
        
        # Se já tem armadura equipada, devolve ao inventário
        if self.equipped_armor:
            self.inventory.append(copy.deepcopy(self.equipped_armor))
            print(f"\n{self.equipped_armor.name} foi desequipada e retornou ao inventário.")
        
        # Remove a nova armadura do inventário se estiver lá
        if armor in self.inventory:
            self.inventory.remove(armor)
        
        self.equipped_armor = armor
        
        # Recalcula mana máxima com novo equipamento
        new_max_mana = self.calculate_max_mana()
        mana_diff = new_max_mana - old_max_mana
        
        self.max_mana = new_max_mana
        self.mana = min(self.mana + mana_diff, self.max_mana)  # Adiciona bônus à mana atual
        
        print(f"\n✅ {armor.name} equipada!")
        print(f"Defesa agora: {self.get_total_defense()}")
        
        # Mostra bônus de mana se houver
        if hasattr(armor, 'mana_bonus') and armor.mana_bonus > 0:
            print(f"✨ Mana Máxima: +{armor.mana_bonus} ({self.mana}/{self.max_mana})")
    
    def unequip_weapon(self):
        """Remove a arma equipada"""
        import copy
        if self.equipped_weapon:
            weapon = self.equipped_weapon
            self.inventory.append(copy.deepcopy(weapon))
            self.equipped_weapon = None
            print(f"\n{weapon.name} foi desequipada e retornou ao inventário.")
            return weapon
        else:
            print("\n❌ Você não tem arma equipada!")
        return None
    
    def unequip_shield(self):
        """Remove o escudo equipado"""
        import copy
        if self.equipped_shield:
            shield = self.equipped_shield
            self.inventory.append(copy.deepcopy(shield))
            self.equipped_shield = None
            print(f"\n{shield.name} foi desequipado e retornou ao inventário.")
            return shield
        else:
            print("\n❌ Você não tem escudo equipado!")
        return None
    
    def unequip_armor(self):
        """Remove a armadura equipada"""
        import copy
        if self.equipped_armor:
            armor = self.equipped_armor
            old_max_mana = self.max_mana
            
            self.inventory.append(copy.deepcopy(armor))
            self.equipped_armor = None
            
            # Recalcula mana máxima sem o equipamento
            new_max_mana = self.calculate_max_mana()
            mana_diff = new_max_mana - old_max_mana
            
            self.max_mana = new_max_mana
            self.mana = min(self.mana, self.max_mana)  # Ajusta mana se exceder o novo máximo
            
            print(f"\n{armor.name} foi desequipada e retornou ao inventário.")
            
            # Mostra perda de mana se houver
            if hasattr(armor, 'mana_bonus') and armor.mana_bonus > 0:
                print(f"✨ Mana Máxima: -{armor.mana_bonus} ({self.mana}/{self.max_mana})")
            
            return armor
        else:
            print("\n❌ Você não tem armadura equipada!")
        return None
    
    def show_status(self):
        """Exibe status completo do jogador"""
        class_icon = "⚔️" if self.player_class == "guerreiro" else "🔮"
        class_name = self.player_class.capitalize()
        
        print(f"\n{'='*40}")
        print(f"👤 {self.name} - Nível {self.level}")
        print(f"{class_icon} Classe: {class_name}")
        print(f"{'='*40}")
        print(f"❤️  HP: {self.hp} / {self.max_hp}")
        print(f"💙 Mana: {self.mana} / {self.max_mana}")
        print(f"⚔️  Ataque: {self.get_total_attack()} (Base: {self.base_attack})")
        print(f"🛡️  Defesa: {self.get_total_defense()} (Base: {self.base_defense})")
        print(f"🌟 Taxa de Crítico: {self.calculate_crit_chance()}%")
        print(f"✨ XP: {self.xp} / {self.get_xp_needed()}")
        print(f"\n📊 Atributos:")
        print(f"  💪 Força: {self.strength}")
        print(f"  ❤️  Vitalidade: {self.vitality}")
        print(f"  ⚡ Agilidade: {self.agility}")
        
        # Exibe bônus de classe
        print(f"\n🎭 Bônus de Classe:")
        if self.player_class == "guerreiro":
            melee_percent = int((self.melee_bonus - 1) * 100)
            magic_percent = int((1 - self.magic_power) * 100)
            print(f"  ⚔️  Dano Corpo a Corpo: +{melee_percent}%")
            print(f"  🔮 Dano Mágico: -{magic_percent}%")
        else:  # mago
            magic_percent = int((self.magic_power - 1) * 100)
            melee_percent = int((1 - self.melee_bonus) * 100)
            print(f"  🔮 Dano Mágico: +{magic_percent}%")
            print(f"  ⚔️  Dano Corpo a Corpo: -{melee_percent}%")
        
        if self.equipped_weapon or self.equipped_shield or self.equipped_armor:
            print(f"\n🎒 Equipamentos:")
            if self.equipped_weapon:
                print(f"  ⚔️  {self.equipped_weapon.name} (+{self.equipped_weapon.attack_bonus} Ataque)")
            if self.equipped_shield:
                print(f"  🛡️  {self.equipped_shield.name} (+{self.equipped_shield.defense_bonus} Defesa)")
            if self.equipped_armor:
                print(f"  🛡️  {self.equipped_armor.name} (+{self.equipped_armor.defense_bonus} Defesa)")
        
        if self.known_spells:
            print(f"\n✨ Magias Conhecidas:")
            for spell in self.known_spells:
                print(f"  🔮 {spell.name} (Custo: {spell.mana_cost} mana)")
        
        print(f"{'='*40}")