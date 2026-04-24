from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from player import Player
from world import World
from save_manager import SaveManager
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Dicionário para armazenar jogos ativos (em memória)
active_games = {}

SPECIAL_BOSS_ROOMS = {
    '14': {
        'boss_name': 'Blackwarrior',
        'display_name': 'Blackwarrior',
        'required_class': 'guerreiro',
        'required_rune': 'blackwarrior',
        'button_label': '🕯️ Invocar Blackwarrior',
        'locked_message': 'O Altar Sombrio só responde a um guerreiro que carregue a runa de invocação correta.',
        'story_template': '{player_name} coloca a {rune_name} sobre o Altar Sombrio e invoca o {boss_name}.',
        'scene_title': 'O Altar Desperta',
        'scene_subtitle': 'A pedra negra responde apenas ao aço e ao juramento do guerreiro.',
        'scene_lines': [
            '{player_name} pressiona a {rune_name} contra o altar e as marcas rúnicas se acendem em âmbar.',
            'Uma armadura vazia se recompõe em meio à fuligem, e {boss_name} ergue a cabeça para encará-lo.',
            'O salão se fecha em silêncio. Não há mais ritual a cumprir, apenas batalha a vencer.'
        ],
        'victory_title': 'O altar silencia.',
        'victory_message': 'A essência de {boss_name} se desfaz em cinzas, revelando um espólio forjado para um guerreiro.'
    },
    '20': {
        'boss_name': 'Necromancer',
        'display_name': 'Necromante',
        'required_class': 'mago',
        'required_rune': 'necromancer',
        'button_label': '🕯️ Invocar Necromante',
        'locked_message': 'A Cripta Profanada só responde a um mago que carregue a runa necromântica.',
        'story_template': '{player_name} coloca a {rune_name} no centro do círculo profano e invoca o {boss_name}.',
        'scene_title': 'A Cripta Respira',
        'scene_subtitle': 'O círculo profano reconhece a runa e chama por um conjurador.',
        'scene_lines': [
            '{player_name} deposita a {rune_name} no centro do círculo, e a poeira dos sarcófagos começa a girar.',
            'Sussurros antigos ecoam pelas pedras quando {boss_name} emerge, envolto em véus de morte e magia.',
            'A energia do ritual aperta sua respiração. Fugir agora significaria ceder a própria alma.'
        ],
        'victory_title': 'A cripta se aquieta.',
        'victory_message': 'Os ecos de {boss_name} se rompem no vazio, deixando para trás relíquias destinadas a um mago.'
    }
}


def clear_current_game():
    """Remove o jogo ativo da sessão atual."""
    game_id = session.get('game_id')
    if game_id:
        active_games.pop(game_id, None)
    session.clear()


def get_special_boss_state(player, world, room_id):
    """Retorna o estado de invocação dos bosses especiais para a interface web."""
    config = SPECIAL_BOSS_ROOMS.get(room_id)
    if not config or room_id in world.defeated_enemies:
        return None

    rune = next(
        (
            item for item in player.inventory
            if item.item_type == 'rune' and getattr(item, 'summon_entity', None) == config['required_rune']
        ),
        None
    )

    can_invoke = player.player_class == config['required_class'] and rune is not None

    return {
        'boss_name': config['boss_name'],
        'display_name': config.get('display_name', config['boss_name']),
        'button_label': config['button_label'],
        'locked_message': None if can_invoke else config['locked_message'],
        'can_invoke': can_invoke,
        'rune': rune,
        'story_template': config['story_template']
    }


def get_multi_enemy_state(world, room_id):
    """Retorna o estado de salas com múltiplos inimigos para a interface web."""
    room = world.get_room(room_id)
    enemies = room.get('enemies') if room else None

    if not room or not enemies or room_id in world.defeated_enemies:
        return None

    return {
        'button_label': '⚔️ Enfrentar os Guardiões Finais',
        'intro_message': f"A {room['name']} guarda uma sequência mortal de adversários.",
        'enemy_names': list(enemies),
    }


def serialize_player_companion(companion):
    """Serializa um companheiro recrutado para a interface web."""
    from companions import get_companion_unlocked_skill_names, get_companion_next_unlock

    unlocked_skill_names = get_companion_unlocked_skill_names(companion)
    next_unlock = get_companion_next_unlock(companion, companion.get('player_level', 1))

    return {
        'id': companion.get('id'),
        'name': companion.get('name', 'Companheiro'),
        'title': companion.get('title', ''),
        'companion_class': companion.get('companion_class', ''),
        'role': companion.get('role', 'apoio'),
        'description': companion.get('description', ''),
        'attack_min': companion.get('attack_min', 0),
        'attack_max': companion.get('attack_max', 0),
        'weapon_name': companion.get('weapon_name'),
        'weapon_bonus': companion.get('weapon_bonus', 0),
        'skills': unlocked_skill_names,
        'next_skill_name': next_unlock.get('name') if next_unlock else None,
        'next_unlock_level': next_unlock.get('unlock_level') if next_unlock else None,
    }


def get_item_registry():
    """Retorna o registro de itens disponível para reconstrução/equipamento."""
    return SaveManager()._get_item_registry()


def serialize_companion_inventory_weapon(item, item_index):
    """Serializa uma arma compatível com companions."""
    return {
        'index': item_index,
        'name': item.name,
        'description': getattr(item, 'description', ''),
        'attack_bonus': getattr(item, 'attack_bonus', 0),
        'companion_class': getattr(item, 'companion_class', None),
    }


def get_available_companion_weapons(player, companion_class):
    """Lista as armas do inventário que podem ser equipadas por um companion."""
    weapons = []
    for idx, item in enumerate(player.inventory):
        if item.item_type != 'weapon':
            continue
        if getattr(item, 'intended_user', 'player') != 'companion':
            continue
        if getattr(item, 'companion_class', None) != companion_class:
            continue
        weapons.append(serialize_companion_inventory_weapon(item, idx))

    return weapons


def serialize_companion_management(companion, player):
    """Serializa companion com mini-arvore e armas disponíveis."""
    from companions import get_companion_skill_nodes, get_companion_available_points, get_companion_next_unlock

    next_unlock = get_companion_next_unlock(companion, player.level)
    base_payload = serialize_player_companion({**companion, 'player_level': player.level})
    base_payload.update({
        'available_points': get_companion_available_points(companion, player.level),
        'skill_nodes': get_companion_skill_nodes(companion, player.level),
        'available_weapons': get_available_companion_weapons(player, companion.get('companion_class')),
        'next_skill_name': next_unlock.get('name') if next_unlock else None,
        'next_unlock_level': next_unlock.get('unlock_level') if next_unlock else None,
    })
    return base_payload


def serialize_room_npc(room, player=None):
    """Serializa um NPC opcional da sala para a interface web."""
    npc = room.get('npc') if room else None
    if not npc:
        return None

    companion_id = npc.get('companion_id')
    if player and companion_id and player.has_companion(companion_id):
        return None

    topics = []
    for topic in npc.get('topics', []):
        label = topic.get('label')
        response = topic.get('response')
        if label and response:
            topics.append({
                'label': label,
                'response': response,
            })

    return {
        'name': npc.get('name', 'Figura Misteriosa'),
        'title': npc.get('title', ''),
        'intro': npc.get('intro', ''),
        'button_label': npc.get('button_label', '💬 Conversar'),
        'can_recruit': bool(companion_id),
        'recruit_button_label': npc.get('recruit_button_label', '🤝 Recrutar'),
        'companion_id': companion_id,
        'topics': topics,
    }


def build_special_boss_intro(player, special_boss, enemy, room_id):
    """Monta os dados da cena de invocação para bosses especiais."""
    config = SPECIAL_BOSS_ROOMS[room_id]
    lines = [
        line.format(
            player_name=player.name,
            rune_name=special_boss['rune'].name,
            boss_name=enemy.name,
        )
        for line in config['scene_lines']
    ]

    return {
        'title': config['scene_title'],
        'subtitle': config['scene_subtitle'],
        'boss_name': enemy.name,
        'action_label': f'⚔️ Enfrentar {enemy.name}',
        'lines': lines,
    }


def serialize_reward_item(item, grant_text):
    """Serializa um item de recompensa para a interface web."""
    return {
        'name': item.name,
        'type': item.item_type,
        'description': getattr(item, 'description', ''),
        'grant_text': grant_text,
    }


def grant_room_rewards(player, world, room_id, source='any'):
    """Entrega as recompensas de uma sala ao jogador."""
    items = world.get_item_from_room(room_id, player.player_class, source=source)
    rewards = []

    for item in items:
        if item.item_type == 'spell':
            learned = player.learn_spell(item)
            grant_text = 'Magia inscrita em sua memória.' if learned else 'O conhecimento já estava selado em sua mente.'
        else:
            added = player.add_to_inventory(item)
            grant_text = 'Relíquia adicionada ao inventário.' if added else 'Relíquia única já estava em sua posse.'

        rewards.append(serialize_reward_item(item, grant_text))

    return rewards


def build_special_boss_reward_summary(room_id, boss_name, rewards):
    """Resume o espólio recebido após derrotar um boss especial."""
    config = SPECIAL_BOSS_ROOMS.get(room_id)
    if not config or not rewards:
        return None

    return {
        'title': config['victory_title'],
        'message': config['victory_message'].format(boss_name=boss_name),
        'items': rewards,
    }


def build_reward_summary(title, message, rewards):
    """Monta um resumo genérico de recompensas."""
    if not rewards:
        return None

    return {
        'title': title,
        'message': message,
        'items': rewards,
    }


def clear_multi_enemy_progress(game_data):
    """Limpa o estado temporário de salas com múltiplos inimigos."""
    game_data.pop('multi_enemy_queue', None)
    game_data.pop('multi_enemy_room_id', None)
    game_data.pop('multi_enemy_total', None)
    game_data.pop('multi_enemy_progress', None)


def sanitize_save_filename(filename):
    """Sanitiza o nome do arquivo de save informado pelo usuário."""
    if not filename:
        return None

    safe_name = ''.join(char if char.isalnum() or char in {'_', '-'} else '_' for char in filename.strip())
    if not safe_name:
        return None
    if not safe_name.endswith('.json'):
        safe_name += '.json'
    return safe_name


def get_current_save_filename(game_data):
    """Retorna o nome do save atualmente vinculado ao jogo ativo."""
    return game_data.get('save_filename')


@app.route('/')
def index():
    """Página inicial - Menu Principal"""
    return render_template('menu.html')


@app.route('/exit')
def exit_game():
    """Encerra a sessão atual e mostra tela de saída."""
    escaped = request.args.get('escaped') == '1'
    clear_current_game()
    return render_template('exit.html', escaped=escaped)


@app.route('/new_game', methods=['GET', 'POST'])
def new_game():
    """Cria um novo jogo"""
    if request.method == 'POST':
        clear_current_game()
        data = request.json
        name = data.get('name', 'Aventureiro')
        player_class = data.get('class', 'guerreiro')
        
        # Cria novo jogador e mundo
        player = Player(name, player_class)
        world = World()
        
        # Gera ID único para a sessão
        game_id = secrets.token_hex(8)
        session['game_id'] = game_id
        
        # Armazena o jogo
        active_games[game_id] = {
            'player': player,
            'world': world,
            'save_filename': None,
        }
        
        return jsonify({'success': True, 'game_id': game_id})
    
    return render_template('new_game.html')


@app.route('/game')
def game():
    """Tela principal do jogo"""
    game_id = session.get('game_id')
    
    if not game_id or game_id not in active_games:
        return redirect(url_for('index'))
    
    return render_template('game.html')


@app.route('/companions')
def companions_page():
    """Tela de gerenciamento dos companions."""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return redirect(url_for('index'))

    return render_template('companions.html')


@app.route('/intro')
def intro():
    """Prólogo narrativo antes do início da aventura."""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return redirect(url_for('index'))

    player = active_games[game_id]['player']
    return render_template('intro.html', player_name=player.name, player_class=player.player_class)


@app.route('/api/game_state')
def get_game_state():
    """Retorna o estado atual do jogo"""
    game_id = session.get('game_id')
    
    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404
    
    game_data = active_games[game_id]
    player = game_data['player']
    world = game_data['world']
    player.sync_companion_progression()

    # Garante progresso do mapa na interface web
    world.visited_rooms.add(player.position)

    room = world.get_room(player.position)
    special_boss = get_special_boss_state(player, world, player.position)
    multi_enemy = get_multi_enemy_state(world, player.position)
    room_npc = serialize_room_npc(room, player)
    has_enemy = world.has_enemy(player.position)

    if special_boss:
        has_enemy = special_boss['can_invoke']
    elif multi_enemy:
        has_enemy = True
    
    return jsonify({
        'player': {
            'name': player.name,
            'class': player.player_class,
            'level': player.level,
            'hp': player.hp,
            'max_hp': player.max_hp,
            'mana': player.mana,
            'max_mana': player.max_mana,
            'max_pa': getattr(player, 'max_pa', 6),
            'xp': player.xp,
            'xp_needed': player.get_xp_needed(),
            'strength': player.strength,
            'vitality': player.vitality,
            'agility': player.agility,
            'crit_chance': player.calculate_crit_chance(),
            'total_attack': player.get_total_attack(),
            'total_defense': player.get_total_defense(),
            'position': player.position,
            'skill_points': player.skill_points,
            'unlocked_skills_count': len(player.unlocked_skills),
            'equipped_weapon': player.equipped_weapon.name if player.equipped_weapon else None,
            'equipped_armor': player.equipped_armor.name if player.equipped_armor else None,
            'equipped_shield': player.equipped_shield.name if player.equipped_shield else None,
            'companions': [
                serialize_player_companion({**companion, 'player_level': player.level})
                for companion in getattr(player, 'companions', [])
            ],
            'current_save_filename': get_current_save_filename(game_data),
        },
        'room': {
            'name': room['name'],
            'description': room['description'],
            'type': room['type'],
            'npc': room_npc,
            'has_enemy': has_enemy,
            'has_treasure': world.has_treasure(player.position),
            'special_boss_name': special_boss['display_name'] if special_boss else None,
            'special_boss_button_label': special_boss['button_label'] if special_boss else None,
            'special_boss_locked_message': special_boss['locked_message'] if special_boss else None,
            'combat_button_label': multi_enemy['button_label'] if multi_enemy else None,
        },
        'directions': world.get_available_directions(player.position)
    })


@app.route('/api/collect_treasure', methods=['POST'])
def collect_treasure():
    """Coleta tesouro do baú da sala atual"""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404

    game_data = active_games[game_id]
    player = game_data['player']
    world = game_data['world']

    room_id = player.position

    if not world.has_treasure(room_id):
        return jsonify({'success': False, 'message': 'Não há baú disponível nesta sala.'})

    items = world.get_item_from_room(room_id, player.player_class, source='chest')

    if not items:
        return jsonify({'success': False, 'message': 'O baú está vazio.'})

    collected = []
    skipped = []
    for item in items:
        added = player.add_to_inventory(item)
        target = collected if added else skipped
        target.append({
            'name': item.name,
            'type': item.item_type,
            'description': getattr(item, 'description', ''),
        })

    if not collected and skipped:
        return jsonify({
            'success': True,
            'message': 'O baú tinha apenas relíquias que você já possuía.',
            'items': [],
            'skipped_items': skipped,
        })

    return jsonify({
        'success': True,
        'message': f'Você coletou {len(collected)} item(ns) do baú!',
        'items': collected,
        'skipped_items': skipped,
    })


@app.route('/api/npc/recruit', methods=['POST'])
def recruit_npc_companion():
    """Recruta o NPC da sala atual como companheiro, quando aplicável."""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404

    game_data = active_games[game_id]
    player = game_data['player']
    world = game_data['world']
    room = world.get_room(player.position)
    npc = room.get('npc') if room else None

    if not npc or not npc.get('companion_id'):
        return jsonify({'success': False, 'message': 'Não há ninguém para libertar nesta sala.'})

    companion_id = npc['companion_id']
    if player.has_companion(companion_id):
        return jsonify({'success': False, 'message': 'Esse aliado já luta ao seu lado.'})

    recruited, companion = player.recruit_companion(companion_id)
    if not recruited or not companion:
        return jsonify({'success': False, 'message': 'Não foi possível recrutar esse companheiro agora.'})

    message = npc.get('recruit_message') or companion.get('join_message') or f"{companion['name']} agora acompanha você."
    return jsonify({
        'success': True,
        'message': message,
        'companion': serialize_player_companion({**companion, 'player_level': player.level}),
    })


@app.route('/api/companions')
def get_companions_data():
    """Retorna dados completos dos companions recrutados."""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404

    player = active_games[game_id]['player']
    player.sync_companion_progression()

    return jsonify({
        'player_level': player.level,
        'companions': [serialize_companion_management(companion, player) for companion in player.companions],
    })


@app.route('/api/companions/unlock_skill', methods=['POST'])
def unlock_companion_skill_api():
    """Desbloqueia manualmente uma skill da mini-arvore de um companion."""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404

    data = request.json or {}
    companion_id = data.get('companion_id')
    skill_id = data.get('skill_id')

    player = active_games[game_id]['player']
    player.sync_companion_progression()

    companion = next((comp for comp in player.companions if comp.get('id') == companion_id), None)
    if not companion:
        return jsonify({'success': False, 'message': 'Companion não encontrado.'})

    from companions import unlock_companion_skill

    success, payload = unlock_companion_skill(companion, skill_id, player.level)
    if not success:
        return jsonify({'success': False, 'message': payload})

    return jsonify({
        'success': True,
        'message': f"{companion['name']} desbloqueou {payload['name']}!",
        'companion': serialize_companion_management(companion, player),
    })


@app.route('/api/companions/equip_weapon', methods=['POST'])
def equip_companion_weapon_api():
    """Equipa uma arma específica de companion a partir do inventário do jogador."""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404

    data = request.json or {}
    companion_id = data.get('companion_id')
    item_index = data.get('item_index')

    try:
        item_index = int(item_index)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Arma inválida.'})

    player = active_games[game_id]['player']
    player.sync_companion_progression()

    companion = next((comp for comp in player.companions if comp.get('id') == companion_id), None)
    if not companion:
        return jsonify({'success': False, 'message': 'Companion não encontrado.'})

    if item_index < 0 or item_index >= len(player.inventory):
        return jsonify({'success': False, 'message': 'Item não encontrado no inventário.'})

    item = player.inventory[item_index]
    if item.item_type != 'weapon' or getattr(item, 'intended_user', 'player') != 'companion':
        return jsonify({'success': False, 'message': 'Esse item não pode ser equipado por companions.'})

    if getattr(item, 'companion_class', None) != companion.get('companion_class'):
        return jsonify({'success': False, 'message': 'Essa arma não pertence à classe desse companion.'})

    previous_weapon_name = companion.get('weapon_item_name')
    if previous_weapon_name:
        previous_item = get_item_registry().get(previous_weapon_name)
        if previous_item:
            player.add_to_inventory(previous_item)

    player.inventory.pop(item_index)
    companion['weapon_name'] = item.name
    companion['weapon_bonus'] = getattr(item, 'attack_bonus', 0)
    companion['weapon_item_name'] = item.name

    return jsonify({
        'success': True,
        'message': f"{companion['name']} equipou {item.name}.",
        'companion': serialize_companion_management(companion, player),
    })


@app.route('/api/move', methods=['POST'])
def move():
    """Move o jogador"""
    game_id = session.get('game_id')
    
    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404
    
    data = request.json
    direction = data.get('direction')
    
    game_data = active_games[game_id]
    player = game_data['player']
    world = game_data['world']
    
    new_room = world.move(player.position, direction)
    
    if new_room:
        player.position = new_room
        world.visited_rooms.add(new_room)
        room_npc = serialize_room_npc(world.get_room(new_room), player)

        if world.is_exit(new_room):
            has_key = any(item.item_type == 'key' for item in player.inventory)
            if has_key:
                return jsonify({
                    'success': True,
                    'message': 'Você alcançou a saída e usou a chave para escapar da dungeon!',
                    'event': 'exit',
                    'redirect_url': url_for('exit_game', escaped=1)
                })

            return jsonify({
                'success': True,
                'message': 'A saída está trancada. Você precisa encontrar a Chave da Saída.',
                'event': 'locked_exit'
            })

        message = f'Você se move para {direction}'
        if room_npc:
            message += f". {room_npc['name']} parece ter algo a dizer."

        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': 'Não é possível ir nessa direção!'})


@app.route('/api/status')
def get_status_data():
    """Retorna status detalhado do jogador e progresso da dungeon"""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404

    game_data = active_games[game_id]
    player = game_data['player']
    world = game_data['world']

    world.visited_rooms.add(player.position)
    total_rooms = len(world.rooms)
    visited_count = len(world.visited_rooms)
    defeated_count = len(world.defeated_enemies)
    looted_count = len(world.looted_rooms)

    return jsonify({
        'player': {
            'name': player.name,
            'class': player.player_class,
            'level': player.level,
            'hp': player.hp,
            'max_hp': player.max_hp,
            'mana': player.mana,
            'max_mana': player.max_mana,
            'max_pa': getattr(player, 'max_pa', 6),
            'xp': player.xp,
            'xp_needed': player.get_xp_needed(),
            'strength': player.strength,
            'vitality': player.vitality,
            'agility': player.agility,
            'crit_chance': player.calculate_crit_chance(),
            'attack': player.get_total_attack(),
            'defense': player.get_total_defense(),
            'skill_points': player.skill_points,
            'attribute_points': getattr(player, 'attribute_points', 0),
            'unlocked_skills_count': len(player.unlocked_skills),
            'position': player.position,
            'equipped': {
                'weapon': player.equipped_weapon.name if player.equipped_weapon else None,
                'shield': player.equipped_shield.name if player.equipped_shield else None,
                'armor': player.equipped_armor.name if player.equipped_armor else None,
            }
        },
        'world': {
            'total_rooms': total_rooms,
            'visited_rooms': visited_count,
            'visited_percent': round((visited_count / total_rooms) * 100, 1) if total_rooms else 0,
            'defeated_enemies': defeated_count,
            'looted_rooms': looted_count,
            'current_room': player.position,
        }
    })


@app.route('/api/status/spend_attribute', methods=['POST'])
def spend_attribute_point():
    """Gasta 1 ponto de atributo via web"""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404

    data = request.json or {}
    attribute = data.get('attribute')

    player = active_games[game_id]['player']
    success, message = player.spend_attribute_point(attribute)

    return jsonify({
        'success': success,
        'message': message,
        'attribute_points': getattr(player, 'attribute_points', 0),
        'stats': {
            'strength': player.strength,
            'vitality': player.vitality,
            'agility': player.agility,
            'max_mana': player.max_mana,
            'hp': player.hp,
            'max_hp': player.max_hp,
            'attack': player.get_total_attack(),
            'defense': player.get_total_defense(),
        }
    })


@app.route('/api/inventory')
def get_inventory():
    """Retorna inventário do jogador"""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404

    player = active_games[game_id]['player']

    items = []
    consumable_groups = {}
    for idx, item in enumerate(player.inventory):
        item_data = {
            'index': idx,
            'name': item.name,
            'type': item.item_type,
            'description': getattr(item, 'description', ''),
            'action': 'equipar',
            'count': 1,
        }

        if item.item_type == 'weapon':
            item_data['attack_bonus'] = getattr(item, 'attack_bonus', 0)
            item_data['intended_user'] = getattr(item, 'intended_user', 'player')
            item_data['companion_class'] = getattr(item, 'companion_class', None)
            item_data['action'] = 'equipar' if item_data['intended_user'] == 'player' else 'info'
        elif item.item_type == 'shield':
            item_data['defense_bonus'] = getattr(item, 'defense_bonus', 0)
            item_data['action'] = 'equipar'
        elif item.item_type == 'armor':
            item_data['defense_bonus'] = getattr(item, 'defense_bonus', 0)
            item_data['mana_bonus'] = getattr(item, 'mana_bonus', 0)
            item_data['action'] = 'equipar'
        elif item.item_type == 'consumable':
            item_data['heal_amount'] = getattr(item, 'heal_amount', 0)
            item_data['action'] = 'usar'
        else:
            item_data['action'] = 'info'

        if item.item_type == 'consumable':
            key = item.name
            if key in consumable_groups:
                consumable_groups[key]['count'] += 1
            else:
                consumable_groups[key] = item_data
                items.append(consumable_groups[key])
        else:
            items.append(item_data)

    return jsonify({
        'items': items,
        'equipped': {
            'weapon': player.equipped_weapon.name if player.equipped_weapon else None,
            'shield': player.equipped_shield.name if player.equipped_shield else None,
            'armor': player.equipped_armor.name if player.equipped_armor else None
        },
        'stats': {
            'hp': player.hp,
            'max_hp': player.max_hp,
            'max_pa': getattr(player, 'max_pa', 6),
            'skill_points': player.skill_points,
            'attack': player.get_total_attack(),
            'defense': player.get_total_defense()
        }
    })


@app.route('/api/inventory/action', methods=['POST'])
def inventory_action():
    """Executa ação em item do inventário (equipar/usar)"""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404

    data = request.json
    item_index = data.get('item_index')

    if item_index is None:
        return jsonify({'success': False, 'message': 'Item inválido'})

    game_data = active_games[game_id]
    player = game_data['player']

    try:
        item_index = int(item_index)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Índice inválido'})

    if item_index < 0 or item_index >= len(player.inventory):
        return jsonify({'success': False, 'message': 'Item não encontrado'})

    item = player.inventory[item_index]

    if item.item_type == 'weapon' and getattr(item, 'intended_user', 'player') != 'player':
        return jsonify({'success': False, 'message': 'Essa arma foi feita para um companion, não para o herói.'})

    if item.item_type == 'consumable':
        success = player.use_item(item_index)
        message = f'{item.name} usado com sucesso!' if success else f'Não foi possível usar {item.name}.'
        return jsonify({'success': success, 'message': message})

    if item.item_type == 'weapon':
        player.equip_weapon(item)
        return jsonify({'success': True, 'message': f'{item.name} equipada!'})

    if item.item_type == 'shield':
        player.equip_shield(item)
        return jsonify({'success': True, 'message': f'{item.name} equipado!'})

    if item.item_type == 'armor':
        player.equip_armor(item)
        return jsonify({'success': True, 'message': f'{item.name} equipada!'})

    return jsonify({'success': False, 'message': 'Este item não tem ação disponível'})


@app.route('/api/save', methods=['POST'])
def save_current_game():
    """Salva o jogo atual em disco."""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404

    data = request.json or {}
    game_data = active_games[game_id]
    current_save_filename = get_current_save_filename(game_data)
    use_current = bool(data.get('use_current')) and current_save_filename
    filename = current_save_filename if use_current else sanitize_save_filename(data.get('filename'))

    save_mgr = SaveManager()
    filepath = save_mgr.save_game(game_data['player'], game_data['world'], filename)

    if not filepath:
        return jsonify({'success': False, 'message': 'Não foi possível salvar o jogo.'})

    saved_filename = os.path.basename(filepath)
    game_data['save_filename'] = saved_filename

    return jsonify({
        'success': True,
        'message': f'Jogo salvo com sucesso em {saved_filename}!',
        'filename': saved_filename,
    })


@app.route('/api/load/<path:filename>', methods=['POST'])
def load_save_file(filename):
    """Carrega um save salvo em disco para a sessão web."""
    save_mgr = SaveManager()
    player, world = save_mgr.load_game(filename)

    if not player or not world:
        return jsonify({'success': False, 'message': 'Não foi possível carregar o save selecionado.'}), 404

    clear_current_game()
    game_id = secrets.token_hex(8)
    session['game_id'] = game_id
    active_games[game_id] = {
        'player': player,
        'world': world,
        'save_filename': filename,
    }

    return jsonify({
        'success': True,
        'redirect_url': url_for('game'),
        'message': f'Save {filename} carregado com sucesso!'
    })


@app.route('/api/map')
def get_map_data():
    """Retorna dados do mapa para renderização web"""
    game_id = session.get('game_id')

    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404

    game_data = active_games[game_id]
    player = game_data['player']
    world = game_data['world']

    from minimap import MiniMap
    mini_map = MiniMap(world)
    positions = mini_map.room_positions

    rooms = []
    for room_id, room in world.rooms.items():
        pos = positions.get(room_id)
        if not pos:
            continue

        visited = room_id in world.visited_rooms or room_id == player.position
        room_type = room.get('type', 'normal')
        is_current = room_id == player.position
        has_enemy = room_id not in world.defeated_enemies and bool(room.get('enemy') or room.get('enemies'))
        has_treasure = room_id not in world.looted_rooms and bool(room.get('items'))

        rooms.append({
            'id': room_id,
            'name': room.get('name', f'Sala {room_id}'),
            'description': room.get('description', ''),
            'type': room_type,
            'row': pos[0],
            'col': pos[1],
            'visited': visited,
            'current': is_current,
            'has_enemy': has_enemy,
            'has_treasure': has_treasure,
            'defeated': room_id in world.defeated_enemies,
            'looted': room_id in world.looted_rooms,
            'connections': [
                {
                    'direction': direction,
                    'target': target_id,
                }
                for direction, target_id in room.get('connections', {}).items()
            ]
        })

    return jsonify({
        'rooms': rooms,
        'current_room': player.position,
        'visited_rooms': list(world.visited_rooms)
    })


@app.route('/skills')
def skills_page():
    """Página da árvore de habilidades"""
    game_id = session.get('game_id')
    
    if not game_id or game_id not in active_games:
        return redirect(url_for('index'))
    
    return render_template('skills.html')


@app.route('/api/skills')
def get_skills():
    """Retorna todas as skills da classe do jogador"""
    game_id = session.get('game_id')
    
    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404
    
    game_data = active_games[game_id]
    player = game_data['player']
    
    # Organizar skills por caminho
    skills_data = {}
    for skill_id, skill in player.skill_tree.get_all_skills().items():
        if skill.path not in skills_data:
            skills_data[skill.path] = []
        
        skills_data[skill.path].append({
            'id': skill_id,
            'name': skill.name,
            'description': skill.description,
            'tier': skill.tier,
            'path': skill.path,
            'cost_pa': get_skill_pa_cost(skill),
            'cooldown': skill.cooldown,
            'power': skill.power,
            'requirements': skill.requirements,
            'is_passive': skill.is_passive,
            'unlocked': skill_id in player.unlocked_skills,
            'can_unlock': skill.can_unlock(player.unlocked_skills)
        })
    
    return jsonify({
        'skills': skills_data,
        'player_class': player.player_class,
        'skill_points': player.skill_points,
        'unlocked_skills': player.unlocked_skills
    })


@app.route('/api/skills/unlock', methods=['POST'])
def unlock_skill():
    """Desbloqueia uma habilidade"""
    game_id = session.get('game_id')
    
    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404
    
    data = request.json
    skill_id = data.get('skill_id')
    
    game_data = active_games[game_id]
    player = game_data['player']
    
    success, message = player.unlock_skill(skill_id)
    
    return jsonify({
        'success': success,
        'message': message,
        'skill_points': player.skill_points,
        'unlocked_skills': player.unlocked_skills
    })


@app.route('/saves')
def saves():
    """Lista saves disponíveis"""
    save_mgr = SaveManager()
    saves_list = save_mgr.list_saves()
    return render_template('saves.html', saves=saves_list)


@app.route('/combat')
def combat_page():
    """Página de combate"""
    game_id = session.get('game_id')
    
    if not game_id or game_id not in active_games:
        return redirect(url_for('index'))
    
    return render_template('combat.html')


@app.route('/api/combat/start', methods=['POST'])
def start_combat():
    """Inicia um combate"""
    game_id = session.get('game_id')
    
    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404
    
    game_data = active_games[game_id]
    player = game_data['player']
    world = game_data['world']
    room = world.get_room(player.position)
    special_boss = get_special_boss_state(player, world, player.position)
    multi_enemy = get_multi_enemy_state(world, player.position)

    if special_boss:
        if not special_boss['can_invoke']:
            return jsonify({'success': False, 'message': special_boss['locked_message']})

        enemy = world.create_enemy_by_name(special_boss['boss_name'])

        if not enemy:
            return jsonify({'success': False, 'message': 'Erro ao invocar o boss especial!'})

        player.remove_from_inventory(special_boss['rune'])

        from combat_pa import CombatPA
        combat = CombatPA(player, enemy)

        game_data['combat'] = combat
        game_data['in_combat'] = True
        game_data['combat_intro'] = special_boss['story_template'].format(
            player_name=player.name,
            rune_name=special_boss['rune'].name,
            boss_name=enemy.name
        )

        return jsonify({
            'success': True,
            'combat_state': get_combat_state_data(combat, player),
            'redirect_url': url_for('combat_page'),
            'special_intro': build_special_boss_intro(player, special_boss, enemy, player.position)
        })

    if multi_enemy:
        enemy_names = multi_enemy['enemy_names']
        first_enemy = world.create_enemy_by_name(enemy_names[0])

        if not first_enemy:
            return jsonify({'success': False, 'message': 'Erro ao iniciar o desafio final!'})

        from combat_pa import CombatPA
        combat = CombatPA(player, first_enemy)

        game_data['combat'] = combat
        game_data['in_combat'] = True
        game_data['combat_intro'] = multi_enemy['intro_message']
        game_data['multi_enemy_queue'] = enemy_names[1:]
        game_data['multi_enemy_room_id'] = player.position
        game_data['multi_enemy_total'] = len(enemy_names)
        game_data['multi_enemy_progress'] = 1

        return jsonify({
            'success': True,
            'combat_state': get_combat_state_data(combat, player),
            'redirect_url': url_for('combat_page')
        })
    
    # Verifica se há inimigo na sala
    if not world.has_enemy(player.position):
        return jsonify({'success': False, 'message': 'Não há inimigo nesta sala!'})
    
    # Cria inimigo
    enemy_name = room.get('enemy')
    
    if not enemy_name:
        return jsonify({'success': False, 'message': 'Inimigo não encontrado!'})
    
    enemy = world.create_enemy_by_name(enemy_name)
    
    if not enemy:
        return jsonify({'success': False, 'message': 'Erro ao criar inimigo!'})
    
    # Cria instância de combate
    from combat_pa import CombatPA
    combat = CombatPA(player, enemy)
    
    # Armazena combate na sessão
    game_data['combat'] = combat
    game_data['in_combat'] = True
    
    return jsonify({
        'success': True,
        'combat_state': get_combat_state_data(combat, player),
        'redirect_url': url_for('combat_page')
    })


@app.route('/api/combat/state')
def get_combat_state_api():
    """Retorna estado atual do combate"""
    game_id = session.get('game_id')
    
    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404
    
    game_data = active_games[game_id]
    
    if not game_data.get('in_combat'):
        return jsonify({'error': 'Não está em combate'}), 404
    
    combat = game_data.get('combat')
    player = game_data['player']
    
    if not combat:
        return jsonify({'error': 'Combate não encontrado'}), 404

    combat_state = get_combat_state_data(combat, player)
    intro_message = game_data.pop('combat_intro', None)
    if intro_message:
        combat_state['intro_message'] = intro_message

    return jsonify(combat_state)


@app.route('/api/combat/action', methods=['POST'])
def combat_action():
    """Executa uma ação de combate"""
    game_id = session.get('game_id')
    
    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404
    
    game_data = active_games[game_id]
    
    if not game_data.get('in_combat'):
        return jsonify({'error': 'Não está em combate'}), 404
    
    combat = game_data.get('combat')
    player = game_data['player']
    
    if not combat:
        return jsonify({'error': 'Combate não encontrado'}), 404
    
    data = request.json
    action = data.get('action')
    
    messages = []
    success = False
    
    if action == 'attack':
        success = combat.player_attack()
        if success:
            messages.append(f"Você atacou {combat.enemy.name}!")
            messages.append("💡 Você ganhará +1 PA extra no próximo turno!")
            messages.append("⏭️ Turno encerrado após ataque.")
    
    elif action == 'defend':
        success = combat.player_defend()
        if success:
            messages.append("🛡️ Você está defendendo!")
            messages.append("⏭️ Seu turno termina automaticamente!")
    
    elif action == 'skill':
        skill_id = data.get('skill_id')
        if skill_id:
            success = combat.player_use_skill(skill_id)
            if success:
                skill = player.skill_tree.get_skill(skill_id)
                messages.append(f"Você usou {skill.name}!")
                messages.append("⏭️ Turno encerrado após habilidade.")
    
    elif action == 'item':
        item_idx = data.get('item_idx')
        if item_idx is not None:
            success = combat.player_use_item(item_idx)
            if success:
                messages.append("Item usado!")
                messages.append("⏭️ Turno encerrado após item.")
    
    elif action == 'flee':
        success = combat.attempt_flee()
        if success:
            messages.append("Você fugiu!")
    
    elif action == 'end_turn':
        # Termina turno do jogador sem zerar PA (preserva PA restante)
        messages.append("⏭️ Turno terminado!")
        success = True

    # Ações que encerram o turno também liberam a ação automática do companheiro.
    if action in ['attack', 'defend', 'skill', 'item', 'end_turn'] and success and not combat.is_combat_over():
        companion_actions = combat.companion_turn()
        for companion_action in companion_actions:
            messages.append(companion_action['message'])
            if companion_action.get('damage', 0) > 0:
                messages.append(f"💥 {companion_action['name']} causou {companion_action['damage']} de dano!")
            if companion_action.get('heal', 0) > 0:
                messages.append(f"💚 {companion_action['name']} restaurou {companion_action['heal']} HP!")
            if companion_action.get('effect') == 'damage_guard':
                messages.append(f"🛡️ {companion_action['name']} reforçou sua defesa para o próximo ataque!")
            if companion_action.get('effect') == 'damage_freeze':
                messages.append(f"❄️ {companion_action['name']} congelou o alvo por um instante!")
            if companion_action.get('effect') == 'damage_poison':
                messages.append(f"☠️ {companion_action['name']} deixou veneno natural agindo no alvo!")

        if not combat.is_combat_over():
            combat.enemy_turn()
            messages.append(f"{combat.enemy.name} realizou suas ações!")

        if not combat.is_combat_over():
            combat.start_player_turn()
            messages.append(f"✨ Novo turno! {combat.player_pa} PA disponível")
    
    # Verifica se combate acabou
    combat_over = combat.is_combat_over()
    result = None
    reward_summary = None
    
    if combat_over:
        result = combat.get_combat_result()
        game_data['in_combat'] = False

        world = game_data['world']
        room_id = player.position
        is_multi_enemy_room = game_data.get('multi_enemy_room_id') == room_id
        
        if result == 'victory':
            player.gain_xp(combat.enemy.xp_reward, auto_distribute=True)
            messages.append(f"Você derrotou {combat.enemy.name}!")
            messages.append(f"+{combat.enemy.xp_reward} XP!")

            if is_multi_enemy_room and game_data.get('multi_enemy_queue'):
                next_enemy_name = game_data['multi_enemy_queue'].pop(0)
                next_enemy = world.create_enemy_by_name(next_enemy_name)

                if not next_enemy:
                    clear_multi_enemy_progress(game_data)
                    return jsonify({
                        'success': False,
                        'messages': messages + ['❌ Erro ao preparar o próximo inimigo.'],
                        'combat_state': get_combat_state_data(combat, player),
                        'combat_over': True,
                        'result': 'defeat',
                        'reward_summary': None
                    })

                player.heal(15)
                player.restore_mana(10)
                from combat_pa import CombatPA
                combat = CombatPA(player, next_enemy)
                game_data['combat'] = combat
                game_data['in_combat'] = True
                game_data['multi_enemy_progress'] = game_data.get('multi_enemy_progress', 1) + 1
                messages.append('💚 Você recupera 15 HP e 10 mana antes do próximo duelo!')
                messages.append(
                    f"⚔️ Próximo combate {game_data['multi_enemy_progress']}/{game_data.get('multi_enemy_total', game_data['multi_enemy_progress'])}: {next_enemy.name}!"
                )
                combat_over = False
                result = None
            else:
                world.defeat_enemy(player.position)

                if room_id in SPECIAL_BOSS_ROOMS:
                    rewards = grant_room_rewards(player, world, room_id, source='boss')
                    reward_summary = build_special_boss_reward_summary(room_id, combat.enemy.name, rewards)
                elif is_multi_enemy_room:
                    rewards = grant_room_rewards(player, world, room_id, source='any')
                    reward_summary = build_reward_summary(
                        'Os guardiões tombaram.',
                        'A câmara final se abriu e o espólio dos duelistas ficou ao seu alcance.',
                        rewards,
                    )
                    clear_multi_enemy_progress(game_data)

        elif is_multi_enemy_room:
            clear_multi_enemy_progress(game_data)
        elif result in {'defeat', 'fled'}:
            clear_multi_enemy_progress(game_data)
    
    return jsonify({
        'success': success,
        'messages': messages,
        'combat_state': get_combat_state_data(combat, player),
        'combat_over': combat_over,
        'result': result,
        'reward_summary': reward_summary
    })


def get_combat_state_data(combat, player):
    """Retorna dados do estado do combate"""
    # Calcula PA do próximo turno
    next_pa = min(combat.player_max_pa, combat.player_pa + 1 + (1 if combat.used_basic_attack else 0))
    
    return {
        'turn': combat.turn_count,
        'player_pa': combat.player_pa,
        'player_max_pa': combat.player_max_pa,
        'used_basic_attack': combat.used_basic_attack,
        'next_turn_pa': next_pa,
        'player': {
            'name': player.name,
            'hp': player.hp,
            'max_hp': player.max_hp,
            'defending': combat.player_defending,
            'status': combat.player_status
        },
        'enemy': {
            'name': combat.enemy.name,
            'hp': combat.enemy.hp,
            'max_hp': combat.enemy.max_hp,
            'defending': combat.enemy_defending,
            'status': combat.enemy_status
        },
        'pa_costs': combat.PA_COSTS,
        'available_skills': get_available_skills(player, combat),
        'available_items': get_available_items(player)
    }


def get_available_skills(player, combat):
    """Retorna lista de skills disponíveis para usar"""
    skills = []
    
    for skill_id in player.unlocked_skills:
        skill = player.skill_tree.get_skill(skill_id)
        
        if skill and not skill.is_passive:
            # Determina custo de PA
            if skill.tier == 'ultimate':
                pa_cost = combat.PA_COSTS['skill_ultimate']
            elif skill.tier == 3:
                pa_cost = combat.PA_COSTS['skill_tier3']
            elif skill.tier == 2:
                pa_cost = combat.PA_COSTS['skill_tier2']
            else:
                pa_cost = combat.PA_COSTS['skill_tier1']
            
            can_use = (combat.player_pa >= pa_cost and skill.current_cooldown == 0)
            
            skills.append({
                'id': skill_id,
                'name': skill.name,
                'description': skill.description,
                'pa_cost': pa_cost,
                'cooldown': skill.current_cooldown,
                'can_use': can_use
            })
    
    return skills


def get_available_items(player):
    """Retorna lista de itens disponíveis para usar"""
    items = []
    
    for idx, item in enumerate(player.inventory):
        if item.item_type in ['potion', 'consumable']:
            items.append({
                'index': idx,
                'name': item.name,
                'description': getattr(item, 'description', '')
            })
    
    return items


def get_skill_pa_cost(skill):
    """Calcula custo de PA de uma skill pelo tier"""
    if skill.tier == 'ultimate':
        return 5
    if skill.tier == 3:
        return 4
    if skill.tier == 2:
        return 3
    return 2


if __name__ == '__main__':
    # Cria pasta de templates se não existir
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("\n" + "="*60)
    print("🎮 DUNGEON OF THE FORGOTTEN - Web Edition")
    print("="*60)
    print("\n🌐 Servidor iniciado!")
    print("📍 Acesse: http://localhost:5050")
    print("\n💡 Pressione Ctrl+C para parar o servidor\n")
    
    app.run(debug=True, host='0.0.0.0', port=5050)
