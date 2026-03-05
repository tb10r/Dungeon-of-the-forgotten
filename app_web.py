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


@app.route('/')
def index():
    """Página inicial - Menu Principal"""
    return render_template('menu.html')


@app.route('/new_game', methods=['GET', 'POST'])
def new_game():
    """Cria um novo jogo"""
    if request.method == 'POST':
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
            'xp': player.xp,
            'position': player.position,
            'skill_points': player.skill_points,
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
        return jsonify({'success': True, 'message': f'Você se move para {direction}'})
    else:
        return jsonify({'success': False, 'message': 'Não é possível ir nessa direção!'})


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
            'cost_mana': skill.cost_mana,
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
    
    elif action == 'defend':
        success = combat.player_defend()
        if success:
            messages.append("🛡️ Você está defendendo!")
            messages.append("⏭️ Seu turno termina automaticamente!")
            
            # Defender termina turno automaticamente
            if not combat.is_combat_over():
                combat.enemy_turn()
                messages.append(f"{combat.enemy.name} realizou suas ações!")
                
                # Regenera PA do jogador
                combat.start_player_turn()
                messages.append(f"✨ Novo turno! {combat.player_pa} PA disponível")
    
    elif action == 'skill':
        skill_id = data.get('skill_id')
        if skill_id:
            success = combat.player_use_skill(skill_id)
            if success:
                skill = player.skill_tree.get_skill(skill_id)
                messages.append(f"Você usou {skill.name}!")
    
    elif action == 'item':
        item_idx = data.get('item_idx')
        if item_idx is not None:
            success = combat.player_use_item(item_idx)
            if success:
                messages.append("Item usado!")
    
    elif action == 'flee':
        success = combat.attempt_flee()
        if success:
            messages.append("Você fugiu!")
    
    elif action == 'end_turn':
        # Termina turno do jogador
        combat.player_pa = 0
        messages.append("⏭️ Turno terminado!")
        success = True
        
        # Turno do inimigo
        if not combat.is_combat_over():
            combat.enemy_turn()
            messages.append(f"{combat.enemy.name} realizou suas ações!")
            
            # Regenera PA do jogador
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
            'mana': player.mana,
            'max_mana': player.max_mana,
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
            
            can_use = (combat.player_pa >= pa_cost and 
                      player.mana >= skill.cost_mana and 
                      skill.current_cooldown == 0)
            
            skills.append({
                'id': skill_id,
                'name': skill.name,
                'description': skill.description,
                'pa_cost': pa_cost,
                'mana_cost': skill.cost_mana,
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


if __name__ == '__main__':
    # Cria pasta de templates se não existir
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("\n" + "="*60)
    print("🎮 DUNGEON OF THE FORGOTTEN - Web Edition")
    print("="*60)
    print("\n🌐 Servidor iniciado!")
    print("📍 Acesse: http://localhost:5000")
    print("\n💡 Pressione Ctrl+C para parar o servidor\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
