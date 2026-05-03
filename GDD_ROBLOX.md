# GDD Roblox - Echoes of the Forgotten

## 1. Visao Geral

Echoes of the Forgotten e um dungeon crawler com progressao de personagem, combate em turnos, loot de salas, bosses especiais, NPCs recrutaveis e companions com miniarvore propria.

Esta versao para Roblox deve manter a identidade do jogo atual, mas adaptar a apresentacao para uma experiencia mais visual, social e clara para sessao curta.

## 2. Elevator Pitch

O jogador entra numa dungeon antiga e avanca por salas conectadas, enfrentando inimigos, abrindo baus, recrutando sobreviventes e derrotando bosses para escapar vivo. Cada classe joga de forma diferente, e companions mudam o ritmo do combate com habilidades automaticas e progressao propria.

## 3. Objetivo do Projeto

Criar uma adaptacao Roblox fiel ao nucleo do jogo atual, com foco em:

- exploracao de dungeon por salas conectadas
- combate em turnos acessivel para Roblox
- progressao de classe com arvore de habilidades
- companions recrutaveis e gerenciaveis
- sessao curta com alto valor de replay

## 4. Fantasia do Jogador

O jogador deve sentir que:

- esta explorando um lugar hostil e cheio de historia
- cada sala pode trazer risco, recompensa ou aliado
- a classe escolhida muda de verdade o jeito de jogar
- companions tornam a equipe mais forte e personalizada
- derrotar bosses especiais e escapar da dungeon e uma conquista clara

## 5. Plataforma e Publico

Plataforma principal: Roblox

Publico alvo:

- jogadores de 10 a 18 anos que gostam de RPG e progressao
- jogadores casuais que preferem partidas de 10 a 25 minutos
- publico que gosta de roguelite leve, dungeon crawler e colecao de habilidades

## 6. Pilares de Design

### 6.1 Exploracao por Salas

O jogo nao deve virar mundo aberto. A forca dele esta no avancar por salas conectadas, com cada sala tendo funcao clara: combate, tesouro, corredor, boss, NPC ou saida.

### 6.2 Combate Tatico Simples

O combate precisa continuar por turnos, com poucas acoes por turno, leitura facil e habilidades com identidade forte.

### 6.3 Progressao Visivel

Subir de nivel, gastar pontos, trocar equipamento e destravar habilidades deve ser rapido de entender e recompensador.

### 6.4 Recrutamento e Equipe

Companions nao sao cosmeticos. Eles devem mudar dano, suporte, controle e defesa da equipe.

### 6.5 Rejogabilidade

Loot aleatorio em baus, classes diferentes e ordem de recompensas precisam incentivar novas runs.

## 7. Estrutura Atual a Preservar

Baseado no jogo atual, a adaptacao deve preservar:

- 3 classes jogaveis: Guerreiro, Mago e Druida
- dungeon com cerca de 31 salas conectadas por grafo
- salas de tesouro, inimigo, boss, corredor, inicio e saida
- bosses especiais Blackwarrior e Necromante
- inimigos comuns como Goblin, Esqueleto e Guardas corrompidos
- loot por sala e itens por classe
- chave de saida e runas especiais
- 3 companions recrutaveis: Alden, Lyra e Eira
- miniarvore de companions e armas exclusivas para companions

## 8. Estrutura da Sessao no Roblox

## 8.1 Fluxo de Sessao

1. Jogador entra no lobby.
2. Escolhe slot ou continua save.
3. Seleciona classe ou entra com personagem ja salvo.
4. Inicia run da dungeon.
5. Explora salas, combate, coleta loot e recruta NPCs.
6. Derrota bosses, encontra a chave e alcanca a saida.
7. Recebe resumo da run, recompensas e progresso salvo.

## 8.2 Duracao Alvo

- MVP: 10 a 20 minutos por run completa
- Full: 20 a 35 minutos por run completa

## 9. Loop Principal

Loop de 30 segundos a 3 minutos:

1. Entrar em uma sala.
2. Ler rapidamente o tipo da sala.
3. Resolver o conteudo da sala.
4. Receber risco ou recompensa.
5. Escolher proxima direcao.

Loop de medio prazo:

1. Ganhar XP.
2. Subir de nivel.
3. Investir atributo e skill.
4. Melhorar equipamento.
5. Fortalecer companions.

Loop de longo prazo:

1. Terminar runs com classes diferentes.
2. Encontrar melhores rotas.
3. Derrotar bosses especiais.
4. Completar equipes diferentes com companions.

## 10. Estrutura de Mundo no Roblox

## 10.1 Recomendacao de Adaptacao

Em vez de menu textual de direcoes, cada sala vira um espaco 3D compacto no Roblox. As conexoes entre salas podem ser representadas por:

- portas fisicas com ProximityPrompt
- corredores curtos com trigger de transicao
- portais rotulados com direcao e nome da proxima sala

## 10.2 Regras do Mapa

- manter a estrutura de grafo do mapa atual
- permitir backtracking
- marcar salas visitadas no minimapa
- travar salas de boss ate condicoes especiais
- travar saida ate o jogador possuir a chave

## 10.3 Zonas Visuais

- Area Inicial
- Area da Cozinha
- Area Central Arcana
- Area de Catacumbas e Cripta
- Area da Torre e Arsenal Secreto
- Camara Final dos Duelistas

## 11. Classes Jogaveis

## 11.1 Guerreiro

Fantasia: linha de frente, dano fisico alto, defesa e critico por presenca.

Caracteristicas:

- mais HP e forca
- bonus de dano corpo a corpo
- menos eficiencia em dano magico

Subarvores:

- Tanque
- DPS
- Berserker

## 11.2 Mago

Fantasia: dano elemental e controle.

Caracteristicas:

- mais mana
- alto dano magico
- menor desempenho em combate fisico

Subarvores:

- Fogo
- Gelo
- Arcano

## 11.3 Druida

Fantasia: equilibrio entre dano natural, suporte e metamorfose.

Caracteristicas:

- estatisticas equilibradas
- dano magico moderado
- boa flexibilidade entre suporte e ofensiva

Subarvores:

- Natureza
- Espiritos
- Metamorfose

## 12. Progressao do Jogador

Ao subir de nivel, o jogador recebe:

- 1 ponto de skill
- 3 pontos de atributo
- 1 ponto adicional de PA maximo

Atributos:

- Forca
- Vitalidade
- Agilidade
- Mana

Valores de leitura para UI:

- HP
- Mana
- Ataque
- Defesa
- Critico
- XP ate proximo nivel

## 13. Combate no Roblox

## 13.1 Decisao de Adaptacao

Recomendacao: manter combate em turnos, mas com apresentacao visual de arena dentro da propria sala ou em uma subarena instanciada.

Motivo:

- preserva o design atual
- facilita balanceamento
- deixa as classes legiveis
- reduz dependencia de animacao e hitbox em tempo real no MVP

## 13.2 Estrutura do Turno

Cada turno do jogador permite 1 acao principal, guiada por custo em PA.

Acoes base:

- atacar
- defender
- usar habilidade
- usar item
- fugir quando permitido
- pular turno

## 13.3 Custos Base de PA

- ataque: 2
- defesa: 1
- item: 1
- habilidade tier 1: 2
- habilidade tier 2: 3
- habilidade tier 3: 4
- habilidade ultimate: 5

## 13.4 Estados e Efeitos

Efeitos a manter:

- queimadura
- congelamento
- veneno
- guard ou defesa temporaria
- cura
- dano com roubo de vida

## 13.5 Formato Visual no Roblox

O combate deve mostrar:

- retrato ou modelo do jogador
- retrato ou modelo do inimigo
- barra de HP e recurso
- botoes grandes de acao
- lista de habilidades destravadas
- fila de cooldowns
- texto curto de log de combate

## 14. Inimigos e Bosses

## 14.1 Inimigos Base

Lista inicial:

- Goblin
- Orc Chief
- Mestre Butcher
- Spaghettus
- Esqueleto
- O Guarda de Prisao Corrompido
- Shadowmage
- Dragonwarrior

## 14.2 Bosses

Bosses principais:

- Orc Chief
- Blackwarrior
- Necromante
- Camara final com dois duelistas

## 14.3 Bosses Especiais

Blackwarrior e Necromante devem exigir condicoes especiais:

- classe correta
- runa correta no inventario
- altar ou cripta como ponto de invocacao

Essa regra e importante porque diferencia a run e reforca fantasia de classe.

## 15. Loot e Economia

## 15.1 Tipos de Item

- armas
- escudos
- armaduras
- consumiveis
- runas
- chave de saida
- magias ou tomos, se forem mantidos como itens desbloqueaveis

## 15.2 Regras de Loot

- baus de tesouro com 2 a 3 itens
- distribuicao aleatoria controlada por pool
- itens especiais unicos por run
- filtragem parcial por classe para manter recompensa relevante

## 15.3 Equipamentos Especiais

Itens unicos de boss devem continuar existindo, como:

- Blackwarrior's Blade
- Blackwarrior's Armor
- Necromancer Robe
- necromancer curser

## 16. Companions

## 16.1 Papel dos Companions

Companions sao aliados recrutaveis que entram na equipe e agem automaticamente no combate.

## 16.2 Companions Iniciais da Adaptacao

- Alden Escudo-Partido: companion guerreiro, vanguarda
- Lyra Cinzaviva: companion maga, artilharia arcana
- Eira Folhaviva: companion druida, suporte natural

## 16.3 Recrutamento

O recrutamento acontece por NPC de sala especifica. No Roblox, isso deve usar:

- ProximityPrompt para iniciar dialogo
- caixa de dialogo com opcao de conversa
- botao de recrutamento quando elegivel

## 16.4 Progressao dos Companions

Cada companion possui:

- 3 habilidades na miniarvore
- skill inicial liberada
- tiers seguintes desbloqueadas por nivel do jogador e gasto manual de ponto
- cooldown proprio por habilidade

## 16.5 Equipamento de Companions

Cada class de companion deve ter arma exclusiva.

Armas iniciais:

- Lamina do Vigia Partido para companion guerreiro
- Foco de Brasa Fria para companion mago
- Totem da Clareira Viva para companion druida

## 17. UI e UX no Roblox

## 17.1 Telas Necessarias

- menu principal
- selecao de classe
- HUD de exploracao
- inventario
- arvore de habilidades do jogador
- tela de companions
- tela de combate
- tela de save ou perfil
- resumo de run

## 17.2 HUD de Exploracao

Elementos:

- HP e Mana
- nivel e XP
- minimapa simplificado
- objetivo atual
- botao de inventario
- botao de habilidades
- botao de companions
- feedback da sala atual

## 17.3 Minimap

O minimapa deve mostrar:

- sala atual
- salas visitadas
- salas especiais conhecidas
- portas ou ligacoes vizinhas

## 17.4 Acessibilidade

- botoes grandes
- pouco texto por interacao
- cores claras para tipo de sala
- feedback sonoro de loot, dano e desbloqueio

## 18. Narrativa e Apresentacao

O tom da narrativa deve continuar sombrio, mas legivel para Roblox.

Diretrizes:

- textos curtos por sala
- dialogos de NPC em 2 a 4 falas por topico
- apresentacao visual forte por zona
- lore entregue por encontros e bosses, nao por parede de texto

## 19. Estrutura Tecnica no Roblox Studio

## 19.1 Organizacao Recomendada

Workspace:

- DungeonRooms
- EnemySpawners
- NPCSpawners
- Portals

ReplicatedStorage:

- Remotes
- SharedModules
- Configs

ServerScriptService:

- DungeonService
- CombatService
- LootService
- CompanionService
- SaveService

StarterGui:

- HUD
- InventoryUI
- SkillTreeUI
- CompanionUI
- CombatUI

StarterPlayerScripts:

- InputController
- UIController
- MapController

## 19.2 Sistemas de Dados

Usar DataStore para progresso persistente.

Salvar:

- classe
- nivel
- atributos
- skills desbloqueadas
- inventario persistente ou metaprogressao, conforme escopo
- companions recrutados
- progresso de companions

No MVP, a run pode ser reiniciada por sessao, mas o perfil deve manter progresso basico.

## 19.3 Logica Autoritativa

Tudo que envolve combate, loot, progressao e save deve ser decidido no servidor.

O cliente apenas:

- envia intencao de acao
- renderiza UI
- toca VFX e SFX

## 20. Escopo de MVP

MVP recomendado para nao explodir escopo:

- 1 lobby simples
- 1 run solo
- 3 classes
- 12 a 15 salas em vez de todas as 31
- 1 boss principal
- 1 boss especial
- 1 companion por classe
- arvore de skills simplificada com 2 tiers por classe
- inventario, loot e save basico

## 21. Escopo de Versao 1.0

- mapa completo com 31 salas
- 3 classes completas
- 3 companions completos
- bosses especiais com runa
- tela de companions completa
- loot por classe e itens de boss
- camara final com multi-inimigo
- minimapa completo

## 22. Riscos de Producao

Principais riscos:

- tentar fazer combate real-time e perder clareza do design atual
- transformar a dungeon em mapa grande demais e perder ritmo
- UI excessivamente complexa para celular
- save persistente grande demais no MVP
- excesso de animacoes antes de o loop principal estar divertido

## 23. Recomendacoes de Producao

Ordem recomendada:

1. prototipo de exploracao por salas
2. prototipo de combate em turnos com 1 classe
3. loot e inventario
4. progressao e skill tree
5. companions
6. bosses especiais
7. save persistente
8. polish visual e monetizacao

## 24. Monetizacao Sugerida

Se houver monetizacao, manter fora do power creep.

Boas opcoes:

- cosmetics de HUD
- skins de arma
- trilhas de pegadas ou VFX cosmetico
- emotes no lobby
- slots extras de save

Evitar no inicio:

- vender vantagem de combate
- vender stats
- pular progressao de boss especial

## 25. Definicao de Sucesso

O projeto sera bem-sucedido se:

- o jogador entende o loop em menos de 5 minutos
- uma run curta ja parece recompensadora
- cada classe parece diferente
- companions parecem uteis e nao enfeite
- a dungeon convida a novas runs

## 26. Proximo Passo Recomendado

Transformar este GDD em um plano de producao Roblox com:

- backlog por sistema
- estrutura de pastas do Roblox Studio
- ordem exata dos scripts e ModuleScripts
- modelo de dados para DataStore
- MVP de 2 semanas ou 4 semanas