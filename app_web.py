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


def clear_current_game():
    """Remove o jogo ativo da sessão atual."""
    game_id = session.get('game_id')
    if game_id:
        active_games.pop(game_id, None)
    session.clear()


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
            'world': world
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


@app.route('/api/game_state')
def get_game_state():
    """Retorna o estado atual do jogo"""
    game_id = session.get('game_id')
    
    if not game_id or game_id not in active_games:
        return jsonify({'error': 'Jogo não encontrado'}), 404
    
    game_data = active_games[game_id]
    player = game_data['player']
    world = game_data['world']

    # Garante progresso do mapa na interface web
    world.visited_rooms.add(player.position)

    room = world.get_room(player.position)
    
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
        },
        'room': {
            'name': room['name'],
            'description': room['description'],
            'type': room['type'],
            'has_enemy': world.has_enemy(player.position),
            'has_treasure': world.has_treasure(player.position),
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
    for item in items:
        player.add_to_inventory(item)
        collected.append({
            'name': item.name,
            'type': item.item_type,
            'description': getattr(item, 'description', '')
        })

    return jsonify({
        'success': True,
        'message': f'Você coletou {len(collected)} item(ns) do baú!',
        'items': collected
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

        return jsonify({'success': True, 'message': f'Você se move para {direction}'})
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
    for idx, item in enumerate(player.inventory):
        item_data = {
            'index': idx,
            'name': item.name,
            'type': item.item_type,
            'description': getattr(item, 'description', ''),
            'action': 'equipar'
        }

        if item.item_type == 'weapon':
            item_data['attack_bonus'] = getattr(item, 'attack_bonus', 0)
            item_data['action'] = 'equipar'
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
        has_enemy = room_id not in world.defeated_enemies and bool(room.get('enemy'))
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
            'connections': list(room.get('connections', {}).values())
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
    
    # Verifica se há inimigo na sala
    if not world.has_enemy(player.position):
        return jsonify({'success': False, 'message': 'Não há inimigo nesta sala!'})
    
    # Cria inimigo
    room = world.get_room(player.position)
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
        'combat_state': get_combat_state_data(combat, player)
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
    
    return jsonify(get_combat_state_data(combat, player))


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
        
        # Turno do inimigo
        if not combat.is_combat_over():
            combat.enemy_turn()
            messages.append(f"{combat.enemy.name} realizou suas ações!")
            
            # Regenera PA do jogador
            combat.start_player_turn()
            messages.append(f"✨ Novo turno! {combat.player_pa} PA disponível")

    # Regra nova: ação válida encerra turno automaticamente (exceto fuga e end_turn)
    if action in ['attack', 'defend', 'skill', 'item'] and success and not combat.is_combat_over():
        combat.enemy_turn()
        messages.append(f"{combat.enemy.name} realizou suas ações!")
        combat.start_player_turn()
        messages.append(f"✨ Novo turno! {combat.player_pa} PA disponível")
    
    # Verifica se combate acabou
    combat_over = combat.is_combat_over()
    result = None
    
    if combat_over:
        result = combat.get_combat_result()
        game_data['in_combat'] = False
        
        if result == 'victory':
            # Marca inimigo como derrotado
            world = game_data['world']
            world.defeat_enemy(player.position)
            player.gain_xp(combat.enemy.xp_reward, auto_distribute=True)
            messages.append(f"Você derrotou {combat.enemy.name}!")
            messages.append(f"+{combat.enemy.xp_reward} XP!")
    
    return jsonify({
        'success': success,
        'messages': messages,
        'combat_state': get_combat_state_data(combat, player),
        'combat_over': combat_over,
        'result': result
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
