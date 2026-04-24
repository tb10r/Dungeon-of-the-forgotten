"""
Sistema de Combate com PA (Action Points) - Inspirado em Clair Obscur: Expedition 33
"""
import random

CRIT_MULTIPLIER = 2.0


class CombatPA:
    """Sistema de combate com pontos de ação"""
    
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.turn_count = 0
        self.combat_active = True
        
        # Sistema de PA
        self.player_max_pa = getattr(player, 'max_pa', 6)  # PA máximo persistente do jogador
        self.enemy_max_pa = 4   # Pontos de ação do inimigo
        
        self.player_pa = self.player_max_pa
        self.enemy_pa = self.enemy_max_pa
        
        # Sistema de defesa temporária
        self.player_defending = False
        self.enemy_defending = False
        
        # Rastreamento de ações para regeneração de PA
        self.used_basic_attack = False
        
        # Status effects
        self.player_status = []  # Lista de efeitos (queimadura, congelamento, etc)
        self.enemy_status = []
    
    # === CUSTOS DE PA ===
    PA_COSTS = {
        'attack': 2,
        'defend': 1,
        'item': 1,
        'skill_tier1': 2,
        'skill_tier2': 3,
        'skill_tier3': 4,
        'skill_ultimate': 5,
        'spell': 2,
        'flee': 2
    }
    
    def start_player_turn(self):
        """Inicia o turno do jogador (regenera PA dinamicamente)"""
        # Regeneração base de PA
        pa_regen = 1
        
        # Bônus de PA se usou ataque básico no turno anterior
        if self.used_basic_attack:
            pa_regen += 1
            print(f"\n⚡ +1 PA extra (usou ataque básico!)")
        
        # Adiciona PA (máximo 6)
        old_pa = self.player_pa
        self.player_pa = min(self.player_max_pa, self.player_pa + pa_regen)
        actual_regen = self.player_pa - old_pa
        
        if actual_regen > 0:
            print(f"✨ +{actual_regen} PA regenerado ({self.player_pa}/{self.player_max_pa})")
        
        # Reset de estado
        self.player_defending = False
        self.used_basic_attack = False
        
        # Tick nos cooldowns das skills
        self.player.tick_skill_cooldowns()
        if hasattr(self.player, 'tick_companion_cooldowns'):
            self.player.tick_companion_cooldowns()
        
        # Aplicar status effects
        self.apply_status_effects(self.player, self.player_status)
    
    def reset_enemy_pa(self):
        """Reseta PA do inimigo no início do turno"""
        self.enemy_pa = self.enemy_max_pa
        self.enemy_defending = False
        
        # Aplicar status effects
        self.apply_status_effects(self.enemy, self.enemy_status)
    
    def apply_status_effects(self, target, status_list):
        """Aplica efeitos de status (queimadura, veneno, etc)"""
        if not status_list:
            return
        
        effects_to_remove = []
        
        for effect in status_list:
            effect_type = effect['type']
            damage = effect.get('damage', 0)
            duration = effect.get('duration', 0)
            
            if effect_type == 'burning':
                target.take_damage(damage)
                print(f"🔥 {target.name if hasattr(target, 'name') else 'Você'} sofre {damage} de dano por queimadura!")
            
            elif effect_type == 'frozen':
                print(f"❄️ {target.name if hasattr(target, 'name') else 'Você'} está congelado!")
                # Perde 1 PA
                if target == self.player:
                    self.player_pa = max(0, self.player_pa - 1)
                else:
                    self.enemy_pa = max(0, self.enemy_pa - 1)
            
            elif effect_type == 'poison':
                target.take_damage(damage)
                print(f"☠️ {target.name if hasattr(target, 'name') else 'Você'} sofre {damage} de dano por veneno!")
            
            # Reduz duração
            effect['duration'] -= 1
            if effect['duration'] <= 0:
                effects_to_remove.append(effect)
                print(f"✨ Efeito {effect_type} acabou!")
        
        # Remove efeitos expirados
        for effect in effects_to_remove:
            status_list.remove(effect)
    
    def has_pa_for_action(self, action_type):
        """Verifica se tem PA suficiente"""
        cost = self.PA_COSTS.get(action_type, 2)
        return self.player_pa >= cost
    
    def consume_pa(self, action_type):
        """Consome PA de uma ação"""
        cost = self.PA_COSTS.get(action_type, 2)
        self.player_pa = max(0, self.player_pa - cost)
        return cost

    def get_weapon_magic_multiplier(self, caster, spell_element=None, skill_path=None):
        """Retorna multiplicador elemental da arma equipada para magia/habilidade."""
        weapon = getattr(caster, 'equipped_weapon', None)
        if not weapon or getattr(weapon, 'elemental_bonus', 0) <= 0:
            return 1.0

        normalized_element = spell_element
        if skill_path == 'arcano':
            normalized_element = 'arcane'
        elif skill_path in {'fogo', 'gelo'}:
            normalized_element = 'fire' if skill_path == 'fogo' else 'ice'

        if weapon.elemental_type == 'all' or weapon.elemental_type == normalized_element:
            print(f"⚡ Bônus da {weapon.name}: +{weapon.elemental_bonus}%!")
            return 1.0 + (weapon.elemental_bonus / 100.0)

        return 1.0

    def get_skill_crit_chance(self, caster, bonuses, crit_multiplier=1.0):
        """Calcula a chance de crítico de uma habilidade do jogador."""
        base_crit = caster.calculate_crit_chance() / 100.0
        passive_crit = bonuses.get('crit_chance', 0) / 100.0
        return min(0.95, (base_crit + passive_crit) * crit_multiplier)

    def apply_warrior_skill_damage(self, skill, caster, target, bonuses):
        """Aplica as habilidades ofensivas do guerreiro com escala de ataque e crítico."""
        skill_id = getattr(skill, 'skill_id', '')
        skill_multiplier = skill.power * bonuses.get('damage_multiplier', 1.0)

        if skill_id == 'w_dps_1':
            crit_chance = self.get_skill_crit_chance(caster, bonuses)
            is_critical = random.random() < crit_chance
            damage = self.calculate_damage(
                int(caster.get_total_attack() * skill_multiplier),
                target.defense,
                is_critical,
                defense_modifier=0.5,
            )
            target.take_damage(damage)
            if is_critical:
                print("🌟 ✨ GOLPE PRECISO CRÍTICO! ✨ 🌟")
            print(f"💥 {damage} de dano!")
            print(f"🩸 {target.name} HP: {target.hp}/{target.max_hp}")
            return damage

        if skill_id == 'w_berserk_2':
            crit_chance = self.get_skill_crit_chance(caster, bonuses)
            is_critical = random.random() < crit_chance
            damage = self.calculate_damage(
                int(caster.get_total_attack() * skill_multiplier),
                target.defense,
                is_critical,
            )
            target.take_damage(damage)
            if is_critical:
                print("🌟 ✨ GOLPE SELVAGEM CRÍTICO! ✨ 🌟")
            print(f"💥 {damage} de dano!")
            print(f"🩸 {target.name} HP: {target.hp}/{target.max_hp}")
            return damage

        multi_hit_skills = {
            'w_dps_3': {'hits': 3, 'crit_multiplier': 1.0},
            'w_dps_ultimate': {'hits': 5, 'crit_multiplier': 2.0},
        }

        if skill_id in multi_hit_skills:
            config = multi_hit_skills[skill_id]
            crit_chance = self.get_skill_crit_chance(caster, bonuses, config['crit_multiplier'])
            total_damage = 0
            print(f"⚔️ {config['hits']} ataques consecutivos!")

            for hit_number in range(config['hits']):
                is_critical = random.random() < crit_chance
                attack_damage = self.calculate_damage(
                    int(caster.get_total_attack() * skill_multiplier),
                    target.defense,
                    is_critical,
                )
                target.take_damage(attack_damage)
                total_damage += attack_damage
                critical_suffix = " CRÍTICO" if is_critical else ""
                print(f"   💥 Ataque {hit_number + 1}: {attack_damage} dano{critical_suffix}")

                if not target.is_alive():
                    break

            print(f"🩸 {target.name} HP: {target.hp}/{target.max_hp}")
            return total_damage

        return None
    
    def calculate_damage(self, attacker_attack, defender_defense, is_critical=False, defense_modifier=1.0):
        """Calcula dano causado"""
        damage = attacker_attack - int(defender_defense * defense_modifier)
        if is_critical:
            damage = int(damage * CRIT_MULTIPLIER)
        return max(1, damage)
    
    def player_attack(self):
        """Ataque básico do jogador (2 PA)"""
        if not self.has_pa_for_action('attack'):
            print(f"❌ PA insuficiente! Necessário: {self.PA_COSTS['attack']}, disponível: {self.player_pa}")
            return False
        
        # Consome PA
        cost = self.consume_pa('attack')
        
        # Calcula bônus passivos
        bonuses = self.player.get_passive_bonuses()
        
        # Verifica crítico
        base_crit_chance = 0.1  # 10% base
        crit_chance = base_crit_chance + (bonuses['crit_chance'] / 100)
        is_critical = random.random() < crit_chance
        
        # Calcula ataque
        base_attack = self.player.get_total_attack()
        attack_with_bonus = int(base_attack * bonuses['damage_multiplier'])
        
        # Calcula defesa do inimigo (se defendendo, +50% defesa)
        defense_modifier = 1.5 if self.enemy_defending else 1.0
        
        damage = self.calculate_damage(
            attack_with_bonus,
            self.enemy.defense,
            is_critical,
            defense_modifier
        )
        
        # Aplicar lifesteal se tiver
        if bonuses['lifesteal'] > 0:
            heal = int(damage * (bonuses['lifesteal'] / 100))
            if heal > 0:
                self.player.restore_hp(heal)
                print(f"💉 Você recupera {heal} HP (Roubo de Vida)")
        
        self.enemy.take_damage(damage)
        
        # Marca que usou ataque básico (para regenerar +1 PA)
        self.used_basic_attack = True
        
        print(f"\n⚔️  Você ataca {self.enemy.name}! (-{cost} PA)")
        print("💡 Você ganhará +1 PA extra no próximo turno!")
        
        if is_critical:
            print("🌟 ✨ ACERTO CRÍTICO! ✨ 🌟")
        
        if self.enemy_defending:
            print(f"🛡️ {self.enemy.name} estava defendendo! (Defesa +50%)")
        
        print(f"💥 Dano causado: {damage}")
        print(f"🩸 {self.enemy.name} HP: {self.enemy.hp}/{self.enemy.max_hp}")
        
        return True
    
    def player_defend(self):
        """Jogador assume postura defensiva (1 PA) - TERMINA O TURNO AUTOMATICAMENTE"""
        if not self.has_pa_for_action('defend'):
            print(f"❌ PA insuficiente! Necessário: {self.PA_COSTS['defend']}, disponível: {self.player_pa}")
            return False
        
        cost = self.consume_pa('defend')
        self.player_defending = True
        
        print(f"\n🛡️ Você assume postura defensiva! (-{cost} PA)")
        print("Defesa aumentada em 50% até o próximo turno!")
        print("⏭️ Seu turno termina automaticamente!")
        
        return True
    
    def player_use_skill(self, skill_id):
        """Usa uma habilidade (consome PA baseado no tier)"""
        skill = self.player.skill_tree.get_skill(skill_id)
        
        if not skill:
            print("❌ Habilidade não encontrada!")
            return False
        
        if skill_id not in self.player.unlocked_skills:
            print("❌ Você não possui esta habilidade!")
            return False
        
        if skill.is_passive:
            print("❌ Esta é uma habilidade passiva!")
            return False
        
        # Determina custo de PA baseado no tier
        if skill.tier == 'ultimate':
            pa_action = 'skill_ultimate'
        elif skill.tier == 3:
            pa_action = 'skill_tier3'
        elif skill.tier == 2:
            pa_action = 'skill_tier2'
        else:
            pa_action = 'skill_tier1'
        
        if not self.has_pa_for_action(pa_action):
            print(f"❌ PA insuficiente! Necessário: {self.PA_COSTS[pa_action]}, disponível: {self.player_pa}")
            return False
        
        # Sem mana: apenas verifica cooldown e ativa skill
        if skill.current_cooldown > 0:
            print(f"❌ {skill.name} ainda está em cooldown! ({skill.current_cooldown} turnos)")
            return False
        skill.current_cooldown = skill.cooldown
        
        # Consome PA
        cost = self.consume_pa(pa_action)
        
        # Aplica efeitos da skill
        print(f"\n⚡ {skill.name}! (-{cost} PA)")
        damage = self.apply_skill_effects(skill, self.player, self.enemy)
        
        return True
    
    def apply_skill_effects(self, skill, caster, target):
        """Aplica efeitos da habilidade"""
        damage = 0
        skill_id = getattr(skill, 'skill_id', '')
        skill_name_lower = skill.name.lower()
        bonuses = caster.get_passive_bonuses()
        effect_kind = getattr(skill, 'effect_kind', None)

        warrior_skill_damage = self.apply_warrior_skill_damage(skill, caster, target, bonuses)
        if warrior_skill_damage is not None:
            damage = warrior_skill_damage
        
        # Habilidades de dano
        if skill.power > 0 and warrior_skill_damage is None and effect_kind != 'heal':
            base_damage = int(skill.power * bonuses['damage_multiplier'])
            skill_path = getattr(skill, 'path', None)
            player_class = getattr(caster, 'player_class', None)

            # Mago aplica poder mágico em habilidades
            if player_class == 'mago':
                base_damage = int(base_damage * getattr(caster, 'magic_power', 1.0))
            elif player_class == 'druida':
                if skill_path in {'natureza', 'espiritos'}:
                    base_damage = int(base_damage * getattr(caster, 'magic_power', 1.0))
                elif skill_path == 'metamorfose':
                    base_damage = int(base_damage * getattr(caster, 'melee_bonus', 1.0))

            base_damage = int(base_damage * self.get_weapon_magic_multiplier(caster, skill_path=skill_path))

            # Buff elemental por caminho da habilidade
            if skill_path == 'fogo':
                base_damage = int(base_damage * bonuses.get('fire_damage_multiplier', 1.0))
            elif skill_path == 'arcano':
                base_damage = int(base_damage * bonuses.get('arcane_damage_multiplier', 1.0))
            
            # Defesa do alvo
            defense_modifier = 1.5 if (target == self.enemy and self.enemy_defending) else 1.0
            damage = self.calculate_damage(base_damage, target.defense, False, defense_modifier)
            
            target.take_damage(damage)
            print(f"💥 {damage} de dano!")
            print(f"🩸 {target.name} HP: {target.hp}/{target.max_hp}")
        
        # Habilidades específicas
        if "bastião eterno" in skill_name_lower or "muralha" in skill_name_lower:
            print(f"🛡️ Defesa aumentada drasticamente!")
            self.player_defending = True

        elif "fogo" in skill_name_lower or "inferno" in skill_name_lower or "chama" in skill_name_lower:
            # Adiciona queimadura
            burn_damage = int(skill.power * 0.2)
            self.enemy_status.append({
                'type': 'burning',
                'damage': burn_damage,
                'duration': 3
            })
            print(f"🔥 {target.name} está queimando! ({burn_damage} dano por 3 turnos)")

        elif "gelo" in skill_name_lower or "inverno" in skill_name_lower or "congelante" in skill_name_lower:
            # Adiciona congelamento
            self.enemy_status.append({
                'type': 'frozen',
                'duration': 2
            })
            print(f"❄️ {target.name} está congelado! (-1 PA por 2 turnos)")

        elif effect_kind == 'heal' or "cura" in skill_name_lower or "regeneração" in skill_name_lower:
            # Cura
            heal = min(skill.power, caster.max_hp - caster.hp)
            caster.heal(heal)
            print(f"💚 Você recupera {heal} HP!")

        elif effect_kind == 'damage_guard':
            self.player_defending = True
            print("🌫️ Espíritos guardiões envolvem seu corpo até o próximo turno!")

        elif effect_kind == 'damage_heal':
            heal = min(getattr(skill, 'secondary_power', 0), caster.max_hp - caster.hp)
            if heal > 0:
                caster.heal(heal)
                print(f"💚 Espíritos restauram {heal} HP!")

        if "raízes" in skill_name_lower:
            self.enemy_status.append({
                'type': 'frozen',
                'duration': 2
            })
            print(f"🌿 {target.name} foi enredado por raízes! (-1 PA por 2 turnos)")

        elif "vinhas" in skill_name_lower or "floresta" in skill_name_lower:
            poison_damage = max(4, int(skill.power * 0.18))
            self.enemy_status.append({
                'type': 'poison',
                'damage': poison_damage,
                'duration': 3
            })
            print(f"☠️ Seiva tóxica corrói {target.name}! ({poison_damage} dano por 3 turnos)")
        
        return damage
    
    def player_use_spell(self, spell_idx):
        """Usa uma magia (2 PA) - Sistema antigo"""
        if not self.has_pa_for_action('spell'):
            print(f"❌ PA insuficiente! Necessário: {self.PA_COSTS['spell']}, disponível: {self.player_pa}")
            return False
        
        if not self.player.known_spells:
            print("❌ Você não conhece nenhuma magia!")
            return False
        
        if spell_idx < 0 or spell_idx >= len(self.player.known_spells):
            print("❌ Magia inválida!")
            return False
        
        spell = self.player.known_spells[spell_idx]
        
        if self.player.mana < spell.mana_cost:
            print(f"❌ Mana insuficiente! Precisa de {spell.mana_cost}, tem {self.player.mana}")
            return False
        
        # Consome PA
        cost = self.consume_pa('spell')
        
        # Lança a magia
        result = spell.cast(self.player, self.enemy)
        print(f"\n{result} (-{cost} PA)")
        
        return True
    
    def player_use_item(self, item_idx):
        """Usa um item (1 PA)"""
        if not self.has_pa_for_action('item'):
            print(f"❌ PA insuficiente! Necessário: {self.PA_COSTS['item']}, disponível: {self.player_pa}")
            return False
        
        if not self.player.inventory:
            print("❌ Inventário vazio!")
            return False
        
        if item_idx < 0 or item_idx >= len(self.player.inventory):
            print("❌ Item inválido!")
            return False
        
        # Consome PA
        cost = self.consume_pa('item')
        
        if self.player.use_item(item_idx):
            print(f"✅ Item usado com sucesso! (-{cost} PA)")
            return True
        else:
            # Devolve PA se falhou
            self.player_pa += cost
            return False
    
    def attempt_flee(self):
        """Tenta fugir (2 PA)"""
        if not self.has_pa_for_action('flee'):
            print(f"❌ PA insuficiente! Necessário: {self.PA_COSTS['flee']}, disponível: {self.player_pa}")
            return False
        
        # Boss não permite fuga
        if not getattr(self.enemy, 'can_flee', True):
            print(f"\n❌ Você não pode fugir de {self.enemy.name}!")
            return False
        
        cost = self.consume_pa('flee')
        
        # 30% de chance de fuga
        if random.random() < 0.3:
            print(f"\n🏃 Você conseguiu fugir de {self.enemy.name}! (-{cost} PA)")
            self.combat_active = False
            return True
        else:
            print(f"\n❌ Você tentou fugir, mas {self.enemy.name} bloqueou! (-{cost} PA)")
            return False

    def companion_turn(self):
        """Executa a ação automática de todos os companheiros ativos."""
        from companions import choose_companion_skill

        if hasattr(self.player, 'sync_companion_progression'):
            self.player.sync_companion_progression()

        companions = list(getattr(self.player, 'companions', []))

        if not companions or not self.enemy.is_alive():
            return []

        actions = []
        for companion in companions:
            if not self.enemy.is_alive():
                break

            skill_id, skill = choose_companion_skill(companion)
            if skill_id and skill:
                companion['skill_cooldowns'][skill_id] = skill.get('cooldown', 0)
                effect = skill.get('effect', 'damage')
                damage = 0
                heal = 0

                if effect != 'heal':
                    base_damage = skill.get('power', companion.get('attack_max', 1)) + companion.get('weapon_bonus', 0)
                    damage = self.calculate_damage(base_damage, self.enemy.defense, False)
                    self.enemy.take_damage(damage)

                if effect in {'heal', 'damage_heal'}:
                    heal = min(skill.get('secondary_power', skill.get('power', 0)), self.player.max_hp - self.player.hp)
                    if heal > 0:
                        self.player.heal(heal)

                if effect == 'damage_guard':
                    self.player_defending = True

                if effect == 'damage_freeze':
                    self.enemy_status.append({
                        'type': 'frozen',
                        'duration': 1,
                    })

                if effect == 'damage_poison':
                    self.enemy_status.append({
                        'type': 'poison',
                        'damage': max(3, skill.get('power', 0) // 4),
                        'duration': 3,
                    })

                actions.append({
                    'name': companion.get('name', 'Companheiro'),
                    'skill_name': skill.get('name'),
                    'message': f"✨ {companion.get('name', 'Companheiro')} usa {skill.get('name')}!",
                    'damage': damage,
                    'heal': heal,
                    'effect': effect,
                })
                continue

            weapon_bonus = companion.get('weapon_bonus', 0)
            min_damage = max(1, companion.get('attack_min', 1) + weapon_bonus)
            max_damage = max(min_damage, companion.get('attack_max', min_damage) + weapon_bonus)
            base_damage = random.randint(min_damage, max_damage)
            damage = self.calculate_damage(base_damage, self.enemy.defense, False)
            self.enemy.take_damage(damage)

            actions.append({
                'name': companion.get('name', 'Companheiro'),
                'message': companion.get(
                    'attack_text',
                    '{name} auxilia você contra {enemy_name}.'
                ).format(
                    name=companion.get('name', 'Companheiro'),
                    enemy_name=self.enemy.name,
                ),
                'damage': damage,
                'heal': 0,
                'effect': 'basic_attack',
            })

        return actions
    
    def enemy_turn(self):
        """Turno do inimigo (IA simples)"""
        print(f"\n{'='*50}")
        print(f"🔴 Turno de {self.enemy.name}")
        print(f"{'='*50}")
        
        self.reset_enemy_pa()
        
        while self.enemy_pa >= 2 and self.enemy.is_alive():
            # IA simples: ataca se tiver PA
            if self.enemy_pa >= 2:
                self.enemy_attack()
            else:
                break
        
        print(f"\n🔵 Fim do turno de {self.enemy.name}")
    
    def enemy_attack(self):
        """Ataque do inimigo"""
        attack_damage = self.enemy.get_attack_damage()
        bonuses = self.player.get_passive_bonuses()
        total_defense = int(self.player.get_total_defense() * bonuses.get('defense_multiplier', 1.0))
        
        # Se player está defendendo, +50% defesa
        defense_modifier = 1.5 if self.player_defending else 1.0
        
        damage = self.calculate_damage(
            attack_damage,
            total_defense,
            False,
            defense_modifier
        )
        
        self.player.take_damage(damage)
        
        print(f"\n🗡️  {self.enemy.name} ataca!")
        
        if self.player_defending:
            print(f"🛡️ Você estava defendendo! (Defesa +50%)")
        
        print(f"💥 Dano recebido: {damage}")
        print(f"❤️  Seu HP: {self.player.hp}/{self.player.max_hp}")
        
        # Consome PA do inimigo
        self.enemy_pa -= 2
    
    def show_combat_status(self):
        """Exibe status do combate com PA"""
        print(f"\n{'='*60}")
        print(f"⚔️  COMBATE - Turno {self.turn_count}")
        print(f"{'='*60}")
        
        # Jogador
        print(f"👤 {self.player.name}")
        print(f"   ❤️  HP: {self.player.hp}/{self.player.max_hp}")
        print(f"   ⚡ PA: {self.player_pa}/{self.player_max_pa}")
        
        if self.player_defending:
            print(f"   🛡️ DEFENDENDO")
        
        if self.player_status:
            effects = ", ".join([e['type'] for e in self.player_status])
            print(f"   ⚠️ Status: {effects}")
        
        print()
        
        # Inimigo
        print(f"👹 {self.enemy.name}")
        print(f"   🩸 HP: {self.enemy.hp}/{self.enemy.max_hp}")
        
        if self.enemy_defending:
            print(f"   🛡️ DEFENDENDO")
        
        if self.enemy_status:
            effects = ", ".join([e['type'] for e in self.enemy_status])
            print(f"   ⚠️ Status: {effects}")
        
        print(f"{'='*60}")
    
    def show_action_menu(self):
        """Mostra menu de ações com custos de PA"""
        print(f"\n🎮 Ações Disponíveis (PA: {self.player_pa}/{self.player_max_pa}):")
        print(f"1 - ⚔️  Atacar (2 PA)")
        print(f"2 - 🛡️  Defender (1 PA)")
        print(f"3 - ⚡ Usar Habilidade (2-5 PA)")
        print(f"4 - 🎒 Usar Item (1 PA)")
        print(f"5 - 🏃 Fugir (2 PA)")
        print(f"0 - ⏭️  Pular Turno")
    
    def player_turn(self):
        """Turno do jogador: apenas 1 ação por turno"""
        self.turn_count += 1
        self.start_player_turn()
        
        print(f"\n🔵 Seu Turno!")
        print(f"⚡ PA Disponível: {self.player_pa}/{self.player_max_pa}")
        print("💡 Regra: qualquer ação válida encerra seu turno.")
        
        # Loop de menu até escolher e executar uma ação válida
        while self.player_pa > 0 and self.player.is_alive() and self.enemy.is_alive() and self.combat_active:
            self.show_combat_status()
            self.show_action_menu()
            
            try:
                choice = input("\nEscolha uma ação: ").strip()
                
                if choice == "1":
                    if self.player_attack():
                        print("⏭️ Turno encerrado após ataque.")
                        break
                
                elif choice == "2":
                    if self.player_defend():
                        # Defender termina turno automaticamente
                        break
                
                elif choice == "3":
                    # Menu de habilidades
                    if not self.player.unlocked_skills:
                        print("\n❌ Você não possui habilidades desbloqueadas!")
                        continue
                    
                    print("\n⚡ Suas Habilidades:")
                    idx = 1
                    skill_list = []
                    
                    for skill_id in self.player.unlocked_skills:
                        skill = self.player.skill_tree.get_skill(skill_id)
                        if skill and not skill.is_passive:
                            # Determina custo de PA
                            if skill.tier == 'ultimate':
                                pa_cost = self.PA_COSTS['skill_ultimate']
                            elif skill.tier == 3:
                                pa_cost = self.PA_COSTS['skill_tier3']
                            elif skill.tier == 2:
                                pa_cost = self.PA_COSTS['skill_tier2']
                            else:
                                pa_cost = self.PA_COSTS['skill_tier1']
                            
                            cooldown_text = f" (CD: {skill.current_cooldown})" if skill.current_cooldown > 0 else ""
                            print(f"{idx} - {skill.name} ({pa_cost} PA){cooldown_text}")
                            print(f"    {skill.description}")
                            skill_list.append(skill_id)
                            idx += 1
                    
                    try:
                        skill_choice = int(input("\nQual habilidade? (0 para cancelar): "))
                        if skill_choice == 0:
                            continue
                        
                        if skill_choice < 1 or skill_choice > len(skill_list):
                            print("❌ Habilidade inválida!")
                            continue
                        
                        if self.player_use_skill(skill_list[skill_choice - 1]):
                            print("⏭️ Turno encerrado após habilidade.")
                            break
                    
                    except (ValueError, IndexError):
                        print("❌ Entrada inválida!")
                        continue
                
                elif choice == "4":
                    # Usar item
                    # Usar item
                    if not self.player.inventory:
                        print("❌ Inventário vazio!")
                        continue
                    
                    self.player.show_inventory()
                    
                    try:
                        item_idx = int(input("\nQual item? (0 para cancelar): ")) - 1
                        if item_idx == -1:
                            continue
                        
                        if self.player_use_item(item_idx):
                            print("⏭️ Turno encerrado após item.")
                            break
                    
                    except (ValueError, IndexError):
                        print("❌ Entrada inválida!")
                        continue
                
                elif choice == "5":
                    # Fugir
                    if self.attempt_flee():
                        break
                
                elif choice == "0":
                    # Pular turno
                    print("\n⏭️ Pulando turno...")
                    break
                
                else:
                    print("❌ Opção inválida!")
            
            except KeyboardInterrupt:
                print("\n\n❌ Combate cancelado!")
                self.combat_active = False
                break
            
            except Exception as e:
                print(f"❌ Erro: {e}")
                continue
        
        # Regeneração no fim do turno
        print(f"\n{'='*50}")
        print("🔄 Fim do seu turno!")
        print(f"{'='*50}")
        
        # HP regen de passivas
        bonuses = self.player.get_passive_bonuses()
        if bonuses['hp_regen'] > 0:
            hp_regen = int(bonuses['hp_regen'])
            self.player.restore_hp(hp_regen)
            print(f"💚 +{hp_regen} HP regenerado (Passiva)")
        
        # Mostra preview de PA para próximo turno
        next_pa = min(self.player_max_pa, self.player_pa + 1 + (1 if self.used_basic_attack else 0))
        print(f"\n💡 Próximo turno: {next_pa} PA (base +1" + (" + ataque básico +1" if self.used_basic_attack else "") + ")")
    
    def is_combat_over(self):
        """Verifica se o combate terminou"""
        if not self.player.is_alive():
            return True
        if not self.enemy.is_alive():
            return True
        if not self.combat_active:
            return True
        return False
    
    def get_combat_result(self):
        """Retorna o resultado do combate"""
        if not self.player.is_alive():
            return "defeat"
        elif not self.enemy.is_alive():
            return "victory"
        elif not self.combat_active:
            return "fled"
        return "ongoing"
    
    def run_combat(self):
        """Executa o combate completo"""
        print(f"\n{'='*60}")
        print(f"⚔️  COMBATE INICIADO!")
        print(f"{'='*60}")
        print(f"\n{self.enemy.description}")
        print(f"\n👹 {self.enemy.name} aparece!")
        print(f"\n💡 Sistema de PA com ritmo tático: 1 ação válida por turno.")
        print(f"💡 Você ainda gerencia PA, mas toda ação encerra seu turno.")
        
        while not self.is_combat_over():
            # Turno do jogador
            self.player_turn()
            
            if self.is_combat_over():
                break
            
            # Turno do inimigo
            if self.combat_active and self.enemy.is_alive():
                input("\n[Pressione Enter para o turno do inimigo]")
                self.enemy_turn()
                
                if not self.is_combat_over():
                    input("\n[Pressione Enter para seu turno]")
        
        return self.end_combat()
    
    def end_combat(self):
        """Finaliza o combate"""
        result = self.get_combat_result()
        
        print(f"\n{'='*60}")
        
        if result == "victory":
            print("🎉 VITÓRIA!")
            print(f"{'='*60}")
            print(f"\nVocê derrotou {self.enemy.name}!")
            
            # Ganha XP
            self.player.gain_xp(self.enemy.xp_reward)
            
            return {
                "result": "victory",
                "xp_gained": self.enemy.xp_reward
            }
        
        elif result == "defeat":
            print("💀 DERROTA!")
            print(f"{'='*60}")
            print(f"\nVocê foi derrotado por {self.enemy.name}...")
            print("GAME OVER")
            
            return {
                "result": "defeat"
            }
        
        elif result == "fled":
            print("🏃 FUGA!")
            print(f"{'='*60}")
            print(f"\nVocê escapou de {self.enemy.name}!")
            
            return {
                "result": "fled"
            }
