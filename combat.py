import random

# Multiplicador de dano crítico
CRIT_MULTIPLIER = 2.0


class Combat:
    """Gerencia combate por turnos entre player e enemy"""
    
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.turn_count = 0
        self.combat_active = True
    
    def calculate_damage(self, attacker_attack, defender_defense, is_critical=False):
        """Calcula dano causado (mínimo 1)"""
        damage = attacker_attack - defender_defense
        if is_critical:
            damage = int(damage * CRIT_MULTIPLIER)
        return max(1, damage)
    
    def player_attack(self):
        """Turno de ataque do jogador"""
        # Verifica se é crítico
        is_critical = self.player.roll_critical_hit()
        
        damage = self.calculate_damage(
            self.player.get_total_attack(),
            self.enemy.defense,
            is_critical
        )
        
        self.enemy.take_damage(damage)
        
        print(f"\n⚔️  Você ataca {self.enemy.name}!")
        
        if is_critical:
            print("🌟 ✨ ACERTO CRÍTICO! ✨ 🌟")
            print(f"💥 Dano causado: {damage} (x{CRIT_MULTIPLIER})")
        else:
            print(f"💥 Dano causado: {damage}")
        
        print(f"🩸 {self.enemy.name} HP: {self.enemy.hp}/{self.enemy.max_hp}")
        
        return damage
    
    def enemy_attack(self):
        """Turno de ataque do inimigo"""
        # Obtém dano do inimigo (pode incluir habilidade especial)
        attack_damage = self.enemy.get_attack_damage()
        
        damage = self.calculate_damage(
            attack_damage,
            self.player.get_total_defense()
        )
        
        self.player.take_damage(damage)
        
        print(f"\n🗡️  {self.enemy.name} ataca!")
        print(f"💥 Dano recebido: {damage}")
        print(f"❤️  Seu HP: {self.player.hp}/{self.player.max_hp}")
        
        return damage
    
    def attempt_flee(self):
        """Tenta fugir do combate"""
        # Boss não permite fuga
        if not getattr(self.enemy, 'can_flee', True):
            print(f"\n❌ Você não pode fugir de {self.enemy.name}!")
            return False
        
        # 10% de chance de fuga para inimigos normais
        if random.random() < 0.1:
            print(f"\n🏃 Você conseguiu fugir de {self.enemy.name}!")
            self.combat_active = False
            return True
        else:
            print(f"\n❌ Você tentou fugir, mas {self.enemy.name} bloqueou!")
            # Inimigo ataca após tentativa de fuga falha
            self.enemy_attack()
            return False
    
    def use_item_in_combat(self, item_index):
        """Usa item durante o combate"""
        if self.player.use_item(item_index):
            print("\n✅ Item usado com sucesso!")
            # Inimigo ataca após usar item
            if self.enemy.is_alive():
                self.enemy_attack()
            return True
        return False
    
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
    
    def show_combat_status(self):
        """Exibe status atual do combate"""
        print(f"\n{'='*40}")
        print(f"⚔️  COMBATE - Turno {self.turn_count}")
        print(f"{'='*40}")
        print(f"👤 {self.player.name}: {self.player.hp}/{self.player.max_hp} HP")
        print(f"👹 {self.enemy.name}: {self.enemy.hp}/{self.enemy.max_hp} HP")
        print(f"{'='*40}")
    
    def show_combat_options(self):
        """Exibe opções de combate"""
        print("\n🎮 Ações de Combate:")
        print("1 - Atacar")
        print("2 - Usar Item")
        print("3 - Fugir")
    
    def player_turn(self):
        """Turno completo do jogador (escolha de ação)"""
        self.turn_count += 1
        self.show_combat_status()
        self.show_combat_options()
        
        while True:
            try:
                choice = input("\nEscolha uma ação: ").strip()
                
                if choice == "1":
                    # Ataca
                    self.player_attack()
                    break
                
                elif choice == "2":
                    # Usa item
                    if not self.player.inventory:
                        print("\n❌ Inventário vazio!")
                        continue
                    
                    self.player.show_inventory()
                    
                    try:
                        item_idx = int(input("\nQual item usar? (0 para cancelar): ")) - 1
                        if item_idx == -1:
                            continue
                        
                        if self.use_item_in_combat(item_idx):
                            break
                    except (ValueError, IndexError):
                        print("\n❌ Item inválido!")
                        continue
                
                elif choice == "3":
                    # Tenta fugir
                    self.attempt_flee()
                    break
                
                else:
                    print("❌ Opção inválida!")
            
            except KeyboardInterrupt:
                print("\n\n❌ Combate cancelado!")
                self.combat_active = False
                break
    
    def run_combat(self):
        """Executa o combate completo"""
        print(f"\n{'='*50}")
        print(f"⚔️  COMBATE INICIADO!")
        print(f"{'='*50}")
        print(f"\n{self.enemy.description}")
        print(f"\n👹 {self.enemy.name} aparece!")
        
        while not self.is_combat_over():
            # Turno do jogador
            self.player_turn()
            
            if self.is_combat_over():
                break
            
            # Turno do inimigo (se player não fugiu)
            if self.combat_active and self.enemy.is_alive():
                input("\n[Pressione Enter para o turno do inimigo]")
                self.enemy_attack()
                
                # Pausa após ataque do inimigo
                if not self.is_combat_over():
                    input("\n[Pressione Enter para seu turno]")
        
        # Resultado final
        return self.end_combat()
    
    def end_combat(self):
        """Finaliza o combate e retorna resultado"""
        result = self.get_combat_result()
        
        print(f"\n{'='*50}")
        
        if result == "victory":
            print("🎉 VITÓRIA!")
            print(f"{'='*50}")
            print(f"\nVocê derrotou {self.enemy.name}!")
            
            # Ganha XP
            self.player.gain_xp(self.enemy.xp_reward)
            
            return {
                "result": "victory",
                "xp_gained": self.enemy.xp_reward
            }
        
        elif result == "defeat":
            print("💀 DERROTA!")
            print(f"{'='*50}")
            print(f"\nVocê foi derrotado por {self.enemy.name}...")
            print("GAME OVER")
            
            return {
                "result": "defeat"
            }
        
        elif result == "fled":
            print("🏃 FUGA!")
            print(f"{'='*50}")
            print(f"\nVocê escapou de {self.enemy.name}!")
            
            return {
                "result": "fled"
            }
        
        return {"result": "unknown"}