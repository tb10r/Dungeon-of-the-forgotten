# Roblox Prototype - Day 2

Arquivos de referência para montar o primeiro loop jogável de Echoes of the Forgotten no Roblox Studio.

Objetivo deste pacote:

- mostrar o nome da sala na HUD
- mostrar o objetivo atual na HUD
- permitir derrotar o Goblin via ProximityPrompt
- permitir abrir o baú via ProximityPrompt
- permitir sair da dungeon quando as condições forem cumpridas

## Estrutura esperada no Roblox Studio

Workspace

- Rooms
  - StartRoom
    - RoomTrigger
  - GoblinRoom
    - RoomTrigger
    - GoblinMarker
      - ProximityPrompt
  - TreasureRoom
    - RoomTrigger
    - ChestMarker
      - ProximityPrompt
  - ExitRoom
    - RoomTrigger
    - ExitMarker
      - ProximityPrompt

ReplicatedStorage

- Remotes
  - RoomChanged
  - ObjectiveChanged
- Configs
  - DungeonConfig (ModuleScript)

ServerScriptService

- Services
  - DungeonService (Script)

StarterGui

- HUD
  - RoomLabel
  - ObjectiveLabel
  - HUDController (LocalScript)

## Nomes importantes

Os nomes abaixo precisam bater exatamente:

- StartRoom
- GoblinRoom
- TreasureRoom
- ExitRoom
- RoomTrigger
- GoblinMarker
- ChestMarker
- ExitMarker
- RoomChanged
- ObjectiveChanged
- DungeonConfig
- DungeonService
- HUDController

## Configuração dos triggers

Para cada RoomTrigger:

- Anchored = true
- CanCollide = false
- Transparency = 1
- CanTouch = true

## Configuração dos prompts

Dentro de cada marcador, adicione um ProximityPrompt.

Sugestão de texto:

- GoblinMarker > ProximityPrompt
  - ActionText = "Atacar"
  - ObjectText = "Goblin"

- ChestMarker > ProximityPrompt
  - ActionText = "Abrir"
  - ObjectText = "Baú"

- ExitMarker > ProximityPrompt
  - ActionText = "Sair"
  - ObjectText = "Saída"

## Onde colar cada arquivo

- roblox_prototype/DungeonConfig.lua -> ReplicatedStorage/Configs/DungeonConfig
- roblox_prototype/DungeonService.server.lua -> ServerScriptService/Services/DungeonService
- roblox_prototype/HUDController.client.lua -> StarterGui/HUD/HUDController

## Fluxo esperado ao testar

1. Jogador entra e vê a Sala Inicial.
2. Jogador entra em GoblinRoom e o objetivo muda para derrotar o Goblin.
3. Ao usar o prompt do Goblin, o objetivo muda para ir ao tesouro.
4. Ao abrir o baú, o objetivo muda para ir à saída.
5. Ao usar a saída, aparece a mensagem de vitória na HUD.