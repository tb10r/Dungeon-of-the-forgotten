import copy


def _build_skill(name, description, unlock_level, cooldown, effect, power, secondary_power=0):
    return {
        'name': name,
        'description': description,
        'unlock_level': unlock_level,
        'cooldown': cooldown,
        'effect': effect,
        'power': power,
        'secondary_power': secondary_power,
    }


COMPANION_TEMPLATES = {
    'warrior_companion': {
        'id': 'warrior_companion',
        'name': 'Alden Escudo-Partido',
        'title': 'Veterano da muralha caída',
        'companion_class': 'guerreiro',
        'role': 'vanguarda',
        'description': 'Um guerreiro sobrevivente das antigas guardas da dungeon. Mesmo ferido, ele ainda sabe abrir espaço com espada e escudo.',
        'attack_min': 8,
        'attack_max': 11,
        'weapon_name': 'Espada Quebrada de Guarda',
        'weapon_bonus': 0,
        'attack_text': '{name} avança sobre {enemy_name} com um corte pesado.',
        'join_message': 'Alden ergue a espada rachada, testa seu peso uma última vez e decide marchar com você.',
        'skill_priority': ['warrior_bulwark_3', 'warrior_guard_2', 'warrior_strike_1'],
        'skills': {
            'warrior_strike_1': _build_skill(
                'Investida do Vigia',
                'Alden rompe a guarda inimiga com uma estocada disciplinada.',
                unlock_level=1,
                cooldown=1,
                effect='damage',
                power=16,
            ),
            'warrior_guard_2': _build_skill(
                'Parede de Escudo',
                'O veterano golpeia o inimigo e reforça sua defesa até o próximo turno.',
                unlock_level=4,
                cooldown=3,
                effect='damage_guard',
                power=19,
            ),
            'warrior_bulwark_3': _build_skill(
                'Última Muralha',
                'Alden concentra o peso do corpo e da armadura em um impacto que abre espaço para o grupo.',
                unlock_level=7,
                cooldown=5,
                effect='damage_guard',
                power=26,
            ),
        },
    },
    'mage_companion': {
        'id': 'mage_companion',
        'name': 'Lyra Cinzaviva',
        'title': 'Erudita do véu arcano',
        'companion_class': 'mago',
        'role': 'artilharia arcana',
        'description': 'Uma maga que sobreviveu escondida entre ruínas e poeira. Seus feitiços são rápidos, secos e precisos.',
        'attack_min': 7,
        'attack_max': 13,
        'weapon_name': 'Foco Arcano Fendido',
        'weapon_bonus': 0,
        'attack_text': '{name} dispara uma rajada arcana contra {enemy_name}.',
        'join_message': 'Lyra fecha o grimório rachado, prende o foco à cintura e aceita lutar ao seu lado.',
        'skill_priority': ['mage_nova_3', 'mage_bind_2', 'mage_bolt_1'],
        'skills': {
            'mage_bolt_1': _build_skill(
                'Seta Cinérea',
                'Lyra converte poeira mágica em um projétil direto e preciso.',
                unlock_level=1,
                cooldown=1,
                effect='damage',
                power=15,
            ),
            'mage_bind_2': _build_skill(
                'Laço de Gelo Pálido',
                'A maga enrijece o ar ao redor do alvo, causando dano e travando seus movimentos.',
                unlock_level=4,
                cooldown=3,
                effect='damage_freeze',
                power=14,
            ),
            'mage_nova_3': _build_skill(
                'Nova de Véu',
                'Lyra faz o foco arcano rachar a própria luz e explode energia sobre o inimigo.',
                unlock_level=7,
                cooldown=5,
                effect='damage',
                power=25,
            ),
        },
    },
    'druid_companion': {
        'id': 'druid_companion',
        'name': 'Eira Folhaviva',
        'title': 'Guardiã do jardim petrificado',
        'companion_class': 'druida',
        'role': 'suporte natural',
        'description': 'Uma druida sobrevivente que escuta a dor das raízes fossilizadas e responde com cura, vinhas e presas.',
        'attack_min': 6,
        'attack_max': 10,
        'weapon_name': 'Cetro de Raiz Clara',
        'weapon_bonus': 0,
        'attack_text': '{name} faz brotar espinhos sob {enemy_name}.',
        'join_message': 'Eira toca a pedra coberta de musgo, escuta o lamento do jardim e decide caminhar com você.',
        'skill_priority': ['druid_beast_3', 'druid_moon_2', 'druid_vine_1'],
        'skills': {
            'druid_vine_1': _build_skill(
                'Vinhas da Clareira',
                'Eira invoca vinhas que rasgam o alvo e deixam seiva tóxica na ferida.',
                unlock_level=1,
                cooldown=1,
                effect='damage_poison',
                power=13,
            ),
            'druid_moon_2': _build_skill(
                'Orvalho da Lua',
                'A druida espalha um orvalho frio que fecha cortes e restaura vigor ao grupo.',
                unlock_level=4,
                cooldown=3,
                effect='heal',
                power=18,
            ),
            'druid_beast_3': _build_skill(
                'Salto da Presa Verde',
                'Eira assume um reflexo bestial, fere o alvo e devolve parte da energia à equipe.',
                unlock_level=7,
                cooldown=5,
                effect='damage_heal',
                power=21,
                secondary_power=8,
            ),
        },
    },
}


def sync_companion_progress(companion, player_level=1):
    """Garante formato consistente sem desbloquear skills extras automaticamente."""
    companion.setdefault('skills', {})
    companion.setdefault('skill_priority', [])
    companion.setdefault('unlocked_skills', [])
    companion.setdefault('skill_cooldowns', {})

    valid_skill_ids = set(companion['skills'].keys())
    unlocked = [skill_id for skill_id in companion.get('unlocked_skills', []) if skill_id in valid_skill_ids]
    ordered_skills = sorted(
        companion['skills'].items(),
        key=lambda item: (item[1].get('unlock_level', 1), item[0]),
    )

    for skill_id, skill in ordered_skills:
        if skill.get('unlock_level', 1) <= 1 and skill_id not in unlocked:
            unlocked.append(skill_id)
        companion['skill_cooldowns'].setdefault(skill_id, 0)

    companion['unlocked_skills'] = unlocked
    return companion


def get_companion_available_points(companion, player_level):
    """Calcula quantos pontos de skill o companion pode gastar manualmente."""
    skills = companion.get('skills', {})
    earned_points = sum(
        1
        for skill in skills.values()
        if skill.get('unlock_level', 1) > 1 and player_level >= skill.get('unlock_level', 1)
    )
    spent_points = sum(
        1
        for skill_id in companion.get('unlocked_skills', [])
        if skills.get(skill_id, {}).get('unlock_level', 1) > 1
    )
    return max(0, earned_points - spent_points)


def get_companion_skill_nodes(companion, player_level):
    """Retorna a mini-arvore do companion com estado de desbloqueio."""
    companion = sync_companion_progress(companion, player_level)
    available_points = get_companion_available_points(companion, player_level)
    unlocked = set(companion.get('unlocked_skills', []))
    ordered_skills = sorted(
        companion.get('skills', {}).items(),
        key=lambda item: (item[1].get('unlock_level', 1), item[0]),
    )

    skill_nodes = []
    previous_skills_unlocked = True
    for skill_id, skill in ordered_skills:
        is_unlocked = skill_id in unlocked
        can_unlock = (
            not is_unlocked
            and available_points > 0
            and player_level >= skill.get('unlock_level', 1)
            and previous_skills_unlocked
        )

        skill_nodes.append({
            'id': skill_id,
            'name': skill.get('name'),
            'description': skill.get('description'),
            'unlock_level': skill.get('unlock_level', 1),
            'cooldown': skill.get('cooldown', 0),
            'current_cooldown': companion.get('skill_cooldowns', {}).get(skill_id, 0),
            'unlocked': is_unlocked,
            'can_unlock': can_unlock,
            'effect': skill.get('effect', 'damage'),
        })

        previous_skills_unlocked = previous_skills_unlocked and is_unlocked

    return skill_nodes


def unlock_companion_skill(companion, skill_id, player_level):
    """Desbloqueia manualmente uma skill do companion, se possível."""
    companion = sync_companion_progress(companion, player_level)
    if skill_id in companion.get('unlocked_skills', []):
        return False, 'Essa habilidade do companion já está desbloqueada.'

    skill_nodes = {node['id']: node for node in get_companion_skill_nodes(companion, player_level)}
    selected_skill = skill_nodes.get(skill_id)
    if not selected_skill:
        return False, 'Habilidade de companion não encontrada.'

    if not selected_skill['can_unlock']:
        return False, 'O nível atual ainda não permite desbloquear essa habilidade.'

    companion['unlocked_skills'].append(skill_id)
    return True, companion['skills'][skill_id]


def tick_companion_cooldowns(companion):
    """Reduz o cooldown das skills do companheiro em 1 turno."""
    for skill_id, cooldown in list(companion.get('skill_cooldowns', {}).items()):
        if cooldown > 0:
            companion['skill_cooldowns'][skill_id] = cooldown - 1


def choose_companion_skill(companion):
    """Escolhe a melhor skill disponível do companheiro."""
    unlocked = set(companion.get('unlocked_skills', []))
    cooldowns = companion.get('skill_cooldowns', {})
    priority = companion.get('skill_priority') or list(companion.get('skills', {}).keys())

    for skill_id in priority:
        if skill_id in unlocked and cooldowns.get(skill_id, 0) == 0:
            return skill_id, companion['skills'].get(skill_id)

    return None, None


def get_companion_unlocked_skill_names(companion):
    """Retorna os nomes das skills já desbloqueadas do companheiro."""
    return [
        companion['skills'][skill_id]['name']
        for skill_id in companion.get('unlocked_skills', [])
        if skill_id in companion.get('skills', {})
    ]


def get_companion_next_unlock(companion, player_level):
    """Retorna a próxima skill que ainda será desbloqueada."""
    locked = [
        skill
        for skill_id, skill in companion.get('skills', {}).items()
        if skill_id not in companion.get('unlocked_skills', [])
    ]

    if not locked:
        return None

    return min(locked, key=lambda skill: skill.get('unlock_level', 99))


def build_companion(companion_id, player_level=1):
    """Cria uma cópia independente dos dados base de um companheiro."""
    template = COMPANION_TEMPLATES.get(companion_id)
    if not template:
        return None

    companion = copy.deepcopy(template)
    companion['skills'] = copy.deepcopy(template.get('skills', {}))
    companion['skill_priority'] = list(template.get('skill_priority', []))
    companion['unlocked_skills'] = []
    companion['skill_cooldowns'] = {}
    return sync_companion_progress(companion, player_level)


def hydrate_companion(companion_data, player_level=1):
    """Atualiza um companheiro salvo com a definição mais recente do template."""
    if not companion_data:
        return None

    companion_id = companion_data.get('id')
    template = COMPANION_TEMPLATES.get(companion_id)
    if not template:
        return copy.deepcopy(companion_data)

    hydrated = build_companion(companion_id, player_level)
    for key, value in companion_data.items():
        if key in {'skills', 'skill_priority'}:
            continue
        hydrated[key] = copy.deepcopy(value)

    hydrated['skills'] = copy.deepcopy(template.get('skills', {}))
    hydrated['skill_priority'] = list(template.get('skill_priority', []))
    hydrated['unlocked_skills'] = list(companion_data.get('unlocked_skills', hydrated.get('unlocked_skills', [])))
    hydrated['skill_cooldowns'] = dict(companion_data.get('skill_cooldowns', hydrated.get('skill_cooldowns', {})))
    return sync_companion_progress(hydrated, player_level)