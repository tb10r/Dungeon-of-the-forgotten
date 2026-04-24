"""
Sistema de Árvore de Habilidades tipo Clair Obscur
"""

class Skill:
    """Representa uma habilidade individual"""

    def __init__(self, skill_id, name, description, skill_type, tier, path,
                 cost_pa=0, cooldown=0, power=0, requirements=None, is_passive=False, **kwargs):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.skill_type = skill_type  # "active" ou "passive"
        self.tier = tier  # 1, 2, 3, ultimate
        self.path = path  # "tanque", "dps", "berserker" | "fogo", "gelo", "arcano"
        # Compatibilidade com dados legados: aceita cost_mana e mapeia para PA.
        if "cost_mana" in kwargs:
            cost_pa = kwargs.pop("cost_mana")
        self.cost_pa = cost_pa
        self.cooldown = cooldown  # Em turnos
        self.power = power  # Dano/Cura/Buff valor
        self.requirements = requirements or []  # IDs das skills necessárias
        self.is_passive = is_passive
        self.effect_kind = kwargs.pop("effect_kind", None)
        self.secondary_power = kwargs.pop("secondary_power", 0)
        self.current_cooldown = 0

    @property
    def cost_mana(self):
        """Alias legado para evitar quebra de chamadas antigas."""
        return self.cost_pa
    
    def can_unlock(self, unlocked_skills):
        """Verifica se pode desbloquear esta skill"""
        if not self.requirements:
            return True
        return all(req in unlocked_skills for req in self.requirements)
    
    def use(self, caster, target=None):
        """Usa a habilidade"""
        if self.current_cooldown > 0:
            return False, f"{self.name} ainda está em cooldown! ({self.current_cooldown} turnos)"
        
        self.current_cooldown = self.cooldown
        return True, None
    
    def tick_cooldown(self):
        """Reduz o cooldown em 1"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


class SkillTree:
    """Árvore de habilidades completa"""
    
    def __init__(self, player_class):
        self.player_class = player_class
        self.skills = {}
        self._load_skills()
    
    def _load_skills(self):
        """Carrega as habilidades baseado na classe"""
        if self.player_class == "guerreiro":
            self._load_warrior_skills()
        elif self.player_class == "mago":
            self._load_mage_skills()
        elif self.player_class == "druida":
            self._load_druid_skills()

    def _load_druid_skills(self):
        """Habilidades do Druida - 3 Caminhos."""

        self.skills["d_nature_1"] = Skill(
            "d_nature_1", "Chicote de Vinhas",
            "Golpeia o inimigo com cipós vivos, causando dano e deixando seiva tóxica na ferida.",
            "active", tier=1, path="natureza",
            cost_mana=18, cooldown=0, power=24
        )

        self.skills["d_nature_2"] = Skill(
            "d_nature_2", "Seiva Renovadora",
            "A natureza refaz suas feridas. Regenera 4% do HP máximo ao fim do turno (passiva).",
            "passive", tier=2, path="natureza",
            requirements=["d_nature_1"], is_passive=True, power=0.04
        )

        self.skills["d_nature_3"] = Skill(
            "d_nature_3", "Raízes Constritoras",
            "Raízes emergem do chão, causam dano e prendem o alvo no lugar por instantes.",
            "active", tier=3, path="natureza",
            cost_mana=34, cooldown=6, power=32,
            requirements=["d_nature_2"]
        )

        self.skills["d_nature_ultimate"] = Skill(
            "d_nature_ultimate", "IRA DA FLORESTA PRIMORDIAL",
            "Uma onda de espinhos, galhos e seiva ancestral devasta o inimigo e o intoxica.",
            "active", tier="ultimate", path="natureza",
            cost_mana=60, cooldown=11, power=92,
            requirements=["d_nature_3"]
        )

        self.skills["d_spirit_1"] = Skill(
            "d_spirit_1", "Luar Restaurador",
            "Invoca um brilho sereno que restaura sua vida imediatamente.",
            "active", tier=1, path="espiritos",
            cost_mana=18, cooldown=2, power=26, effect_kind="heal"
        )

        self.skills["d_spirit_2"] = Skill(
            "d_spirit_2", "Ressonância Espiritual",
            "Os ecos do véu fortalecem suas técnicas druidicas em 18% (passiva).",
            "passive", tier=2, path="espiritos",
            requirements=["d_spirit_1"], is_passive=True, power=0.18
        )

        self.skills["d_spirit_3"] = Skill(
            "d_spirit_3", "Névoa Guardiã",
            "Uma névoa espiritual fere o inimigo e cobre seu corpo com proteção ancestral.",
            "active", tier=3, path="espiritos",
            cost_mana=30, cooldown=6, power=24, effect_kind="damage_guard",
            requirements=["d_spirit_2"]
        )

        self.skills["d_spirit_ultimate"] = Skill(
            "d_spirit_ultimate", "CORTEJO DOS ANTIGOS",
            "Espíritos antigos atravessam o alvo, causando dano e devolvendo vigor ao druida.",
            "active", tier="ultimate", path="espiritos",
            cost_mana=58, cooldown=12, power=78, effect_kind="damage_heal", secondary_power=30,
            requirements=["d_spirit_3"]
        )

        self.skills["d_shape_1"] = Skill(
            "d_shape_1", "Garras do Lobo",
            "Canaliza o instinto predatório e desfere um ataque feroz com as mãos transfiguradas.",
            "active", tier=1, path="metamorfose",
            cost_mana=16, cooldown=0, power=20
        )

        self.skills["d_shape_2"] = Skill(
            "d_shape_2", "Pele de Casca",
            "Sua pele endurece como madeira antiga, elevando a defesa em 25% (passiva).",
            "passive", tier=2, path="metamorfose",
            requirements=["d_shape_1"], is_passive=True, power=0.25
        )

        self.skills["d_shape_3"] = Skill(
            "d_shape_3", "Bote Feral",
            "Você avança em salto bestial e rasga a defesa do inimigo com violência.",
            "active", tier=3, path="metamorfose",
            cost_mana=34, cooldown=5, power=36,
            requirements=["d_shape_2"]
        )

        self.skills["d_shape_ultimate"] = Skill(
            "d_shape_ultimate", "AVATAR DA PRESA ANCESTRAL",
            "Assume uma forma predatória suprema e dilacera o inimigo com força esmagadora.",
            "active", tier="ultimate", path="metamorfose",
            cost_mana=62, cooldown=13, power=96,
            requirements=["d_shape_3"]
        )
    
    def _load_warrior_skills(self):
        """Habilidades do Guerreiro - 3 Caminhos"""
        
        # === CAMINHO TANQUE ===
        self.skills["w_tank_1"] = Skill(
            "w_tank_1", "Defesa Férrea", 
            "Reduz 40% do dano recebido por 3 turnos.",
            "active", tier=1, path="tanque",
            cost_mana=15, cooldown=5, power=0.4
        )
        
        self.skills["w_tank_2"] = Skill(
            "w_tank_2", "Escudo Vivo",
            "Recupera 3% HP máximo por turno (passiva).",
            "passive", tier=2, path="tanque",
            requirements=["w_tank_1"], is_passive=True, power=0.03
        )
        
        self.skills["w_tank_3"] = Skill(
            "w_tank_3", "Muralha Impenetrável",
            "Absorve todo o dano do próximo ataque.",
            "active", tier=3, path="tanque",
            cost_mana=30, cooldown=7, requirements=["w_tank_2"]
        )
        
        self.skills["w_tank_ultimate"] = Skill(
            "w_tank_ultimate", "BASTIÃO ETERNO",
            "Torna-se imune a dano por 2 turnos. Reflete 50% do dano bloqueado.",
            "active", tier="ultimate", path="tanque",
            cost_mana=50, cooldown=10, power=0.5,
            requirements=["w_tank_3"]
        )
        
        # === CAMINHO DPS ===
        self.skills["w_dps_1"] = Skill(
            "w_dps_1", "Golpe Preciso",
            "Ataque que ignora 50% da defesa inimiga.",
            "active", tier=1, path="dps",
            cost_mana=20, cooldown=3, power=1.5
        )
        
        self.skills["w_dps_2"] = Skill(
            "w_dps_2", "Mestre de Armas",
            "+15% chance de crítico (passiva).",
            "passive", tier=2, path="dps",
            requirements=["w_dps_1"], is_passive=True, power=15
        )
        
        self.skills["w_dps_3"] = Skill(
            "w_dps_3", "Investida Furiosa",
            "Desfere 3 ataques rápidos consecutivos.",
            "active", tier=3, path="dps",
            cost_mana=35, cooldown=6, power=0.7,
            requirements=["w_dps_2"]
        )
        
        self.skills["w_dps_ultimate"] = Skill(
            "w_dps_ultimate", "TEMPESTADE DE LÂMINAS",
            "5 ataques devastadores com chance de crítico dobrada.",
            "active", tier="ultimate", path="dps",
            cost_mana=60, cooldown=12, power=0.8,
            requirements=["w_dps_3"]
        )
        
        # === CAMINHO BERSERKER ===
        self.skills["w_berserk_1"] = Skill(
            "w_berserk_1", "Fúria Crescente",
            "Quanto menor seu HP, mais dano causa (+2% por 1% HP perdido).",
            "passive", tier=1, path="berserker",
            is_passive=True, power=2
        )
        
        self.skills["w_berserk_2"] = Skill(
            "w_berserk_2", "Golpe Selvagem",
            "Ataque brutal com 200% de dano, mas reduz 20% de sua defesa.",
            "active", tier=2, path="berserker",
            cost_mana=25, cooldown=4, power=2.0,
            requirements=["w_berserk_1"]
        )
        
        self.skills["w_berserk_3"] = Skill(
            "w_berserk_3", "Sede de Sangue",
            "Cura 20% do dano causado (passiva).",
            "passive", tier=3, path="berserker",
            is_passive=True, power=0.2,
            requirements=["w_berserk_2"]
        )
        
        self.skills["w_berserk_ultimate"] = Skill(
            "w_berserk_ultimate", "RAIVA PRIMORDIAL",
            "Entra em fúria extrema: +150% dano, +50% velocidade, ignora dor por 4 turnos.",
            "active", tier="ultimate", path="berserker",
            cost_mana=40, cooldown=15, power=1.5,
            requirements=["w_berserk_3"]
        )
    
    def _load_mage_skills(self):
        """Habilidades do Mago - 3 Caminhos"""
        
        # === CAMINHO FOGO ===
        self.skills["m_fire_1"] = Skill(
            "m_fire_1", "Bola de Fogo",
            "Lança uma bola de fogo causando 25 de dano + queimadura (5 dano/turno por 3 turnos).",
            "active", tier=1, path="fogo",
            cost_mana=20, cooldown=0, power=25
        )
        
        self.skills["m_fire_2"] = Skill(
            "m_fire_2", "Combustão Interna",
            "Magias de fogo causam +30% de dano (passiva).",
            "passive", tier=2, path="fogo",
            requirements=["m_fire_1"], is_passive=True, power=0.3
        )
        
        self.skills["m_fire_3"] = Skill(
            "m_fire_3", "Chuva de Meteoros",
            "3 meteoros caem causando 40 de dano cada.",
            "active", tier=3, path="fogo",
            cost_mana=50, cooldown=8, power=40,
            requirements=["m_fire_2"]
        )
        
        self.skills["m_fire_ultimate"] = Skill(
            "m_fire_ultimate", "INFERNO APOCALÍPTICO",
            "Convoca um inferno massivo causando 150 de dano. Inimigos queimam por 15 dano/turno.",
            "active", tier="ultimate", path="fogo",
            cost_mana=80, cooldown=12, power=150,
            requirements=["m_fire_3"]
        )
        
        # === CAMINHO GELO ===
        self.skills["m_ice_1"] = Skill(
            "m_ice_1", "Lança de Gelo",
            "Projétil gélido causa 20 de dano e reduz velocidade inimiga em 30%.",
            "active", tier=1, path="gelo",
            cost_mana=18, cooldown=0, power=20
        )
        
        self.skills["m_ice_2"] = Skill(
            "m_ice_2", "Congelar",
            "Congela o inimigo por 1 turno (não pode agir).",
            "active", tier=2, path="gelo",
            cost_mana=30, cooldown=5, power=1,
            requirements=["m_ice_1"]
        )
        
        self.skills["m_ice_3"] = Skill(
            "m_ice_3", "Armadura de Gelo",
            "Cria uma armadura que absorve 50 de dano. Dura até quebrar.",
            "active", tier=3, path="gelo",
            cost_mana=35, cooldown=6, power=50,
            requirements=["m_ice_2"]
        )
        
        self.skills["m_ice_ultimate"] = Skill(
            "m_ice_ultimate", "ERA GLACIAL",
            "Congela tudo. 100 de dano + congela por 2 turnos + reduz defesa em 50%.",
            "active", tier="ultimate", path="gelo",
            cost_mana=75, cooldown=15, power=100,
            requirements=["m_ice_3"]
        )
        
        # === CAMINHO ARCANO ===
        self.skills["m_arcane_1"] = Skill(
            "m_arcane_1", "Mísseis Arcanos",
            "3 mísseis mágicos teleguiados, 12 de dano cada.",
            "active", tier=1, path="arcano",
            cost_mana=22, cooldown=1, power=12
        )
        
        self.skills["m_arcane_2"] = Skill(
            "m_arcane_2", "Maestria Arcana",
            "Sua energia flui melhor: técnicas arcanas ficam mais eficientes (passiva).",
            "passive", tier=2, path="arcano",
            requirements=["m_arcane_1"], is_passive=True, power=0.2
        )
        
        self.skills["m_arcane_3"] = Skill(
            "m_arcane_3", "Drenar Essência",
            "Absorve 35 de HP do inimigo e fortalece seu ritmo de ação.",
            "active", tier=3, path="arcano",
            cost_mana=25, cooldown=5, power=35,
            requirements=["m_arcane_2"]
        )
        
        self.skills["m_arcane_ultimate"] = Skill(
            "m_arcane_ultimate", "SINGULARIDADE ARCANA",
            "Cria um vórtice mágico: 120 de dano e acelera seu fluxo de ações.",
            "active", tier="ultimate", path="arcano",
            cost_mana=70, cooldown=14, power=120,
            requirements=["m_arcane_3"]
        )
    
    def get_skill(self, skill_id):
        """Retorna uma skill pelo ID"""
        return self.skills.get(skill_id)
    
    def get_skills_by_tier(self, tier):
        """Retorna todas as skills de um tier"""
        return {k: v for k, v in self.skills.items() if v.tier == tier}
    
    def get_skills_by_path(self, path):
        """Retorna todas as skills de um caminho"""
        return {k: v for k, v in self.skills.items() if v.path == path}
    
    def get_all_skills(self):
        """Retorna todas as skills"""
        return self.skills


# Funções auxiliares para combate
def apply_skill_effects(skill, caster, target):
    """Aplica os efeitos de uma habilidade"""
    effects = []
    
    # Implementar efeitos específicos baseado na skill
    if "Bola de Fogo" in skill.name:
        damage = int(skill.power * getattr(caster, 'magic_power', 1.0))
        target.take_damage(damage)
        effects.append(f"💥 {damage} de dano!")
        # Adicionar queimadura (implementar sistema de status depois)
        effects.append(f"🔥 Alvo está queimando!")
    
    elif "Defesa" in skill.name:
        effects.append(f"🛡️ Defesa aumentada temporariamente!")
    
    return effects
