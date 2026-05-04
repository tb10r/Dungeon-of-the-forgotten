local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local remotesFolder = ReplicatedStorage:WaitForChild("Remotes")
local roomChangedEvent = remotesFolder:WaitForChild("RoomChanged")
local objectiveChangedEvent = remotesFolder:WaitForChild("ObjectiveChanged")

local config = require(ReplicatedStorage:WaitForChild("Configs"):WaitForChild("DungeonConfig"))
local roomsFolder = workspace:WaitForChild(config.RoomsFolderName)

local playerState = {}

local function getState(player)
	if not playerState[player] then
		playerState[player] = {
			currentRoom = "StartRoom",
			goblinDefeated = false,
			chestOpened = false,
			runComplete = false,
		}
	end

	return playerState[player]
end

local function pushHud(player)
	local state = getState(player)
	local roomName = state.currentRoom or "StartRoom"
	local displayName = config.RoomDisplayNames[roomName] or roomName
	local objectiveText = config.getObjective(roomName, state)

	roomChangedEvent:FireClient(player, displayName)
	objectiveChangedEvent:FireClient(player, objectiveText)
end

local function setCurrentRoom(player, roomName)
	local state = getState(player)

	if state.currentRoom == roomName then
		return
	end

	state.currentRoom = roomName
	pushHud(player)
end

local function getPlayerFromHit(hit)
	local character = hit:FindFirstAncestorOfClass("Model")
	if not character then
		return nil
	end

	local humanoid = character:FindFirstChildOfClass("Humanoid")
	if not humanoid then
		return nil
	end

	return Players:GetPlayerFromCharacter(character)
end

local function connectRoomTrigger(roomModel)
	local trigger = roomModel:FindFirstChild(config.TriggerName, true)
	if not trigger or not trigger:IsA("BasePart") then
		warn("RoomTrigger não encontrado em " .. roomModel.Name)
		return
	end

	trigger.Touched:Connect(function(hit)
		local player = getPlayerFromHit(hit)
		if not player then
			return
		end

		setCurrentRoom(player, roomModel.Name)
	end)
	end

local function bindPrompt(roomName, markerName, callback)
	local room = roomsFolder:FindFirstChild(roomName)
	if not room then
		warn("Sala não encontrada: " .. roomName)
		return
	end

	local marker = room:FindFirstChild(markerName, true)
	if not marker then
		warn("Marcador não encontrado: " .. markerName)
		return
	end

	local prompt = marker:FindFirstChildOfClass("ProximityPrompt")
	if not prompt then
		warn("ProximityPrompt não encontrado em " .. markerName)
		return
	end

	prompt.Triggered:Connect(function(player)
		callback(player, prompt)
	end)
end

local function defeatGoblin(player)
	local state = getState(player)
	if state.goblinDefeated then
		pushHud(player)
		return
	end

	state.goblinDefeated = true
	if state.currentRoom == "GoblinRoom" then
		objectiveChangedEvent:FireClient(player, "Goblin derrotado. Vá até a sala do tesouro.")
	else
		pushHud(player)
	end
	end

local function openChest(player)
	local state = getState(player)

	if not state.goblinDefeated then
		objectiveChangedEvent:FireClient(player, "Antes do baú, derrote o Goblin.")
		return
	end

	if state.chestOpened then
		pushHud(player)
		return
	end

	state.chestOpened = true
	if state.currentRoom == "TreasureRoom" then
		objectiveChangedEvent:FireClient(player, "Você encontrou uma recompensa. Vá até a saída.")
	else
		pushHud(player)
	end
	end

local function tryExit(player)
	local state = getState(player)

	if not state.goblinDefeated then
		objectiveChangedEvent:FireClient(player, "A saída continua bloqueada. Derrote o Goblin primeiro.")
		return
	end

	if not state.chestOpened then
		objectiveChangedEvent:FireClient(player, "A saída continua bloqueada. Abra o baú primeiro.")
		return
	end

	state.runComplete = true
	objectiveChangedEvent:FireClient(player, "Vitória! Você escapou da dungeon.")
	end

for _, roomModel in ipairs(roomsFolder:GetChildren()) do
	if roomModel:IsA("Model") then
		connectRoomTrigger(roomModel)
	end
end

bindPrompt("GoblinRoom", config.Markers.Goblin, function(player)
	defeatGoblin(player)
end)

bindPrompt("TreasureRoom", config.Markers.Chest, function(player)
	openChest(player)
end)

bindPrompt("ExitRoom", config.Markers.Exit, function(player)
	tryExit(player)
end)

Players.PlayerAdded:Connect(function(player)
	getState(player)

	player.CharacterAdded:Connect(function()
		task.wait(0.25)
		pushHud(player)
	end)
end)

Players.PlayerRemoving:Connect(function(player)
	playerState[player] = nil
end)