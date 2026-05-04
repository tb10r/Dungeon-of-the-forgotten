local DungeonConfig = {}

DungeonConfig.RoomDisplayNames = {
	StartRoom = "Sala Inicial",
	GoblinRoom = "Sala do Goblin",
	TreasureRoom = "Sala do Tesouro",
	ExitRoom = "Saída",
}

DungeonConfig.DefaultObjectives = {
	StartRoom = "Explore a dungeon.",
	GoblinRoom = "Derrote o Goblin.",
	TreasureRoom = "Abra o baú.",
	ExitRoom = "Encontre uma forma de escapar.",
}

DungeonConfig.RoomsFolderName = "Rooms"
DungeonConfig.TriggerName = "RoomTrigger"

DungeonConfig.Markers = {
	Goblin = "GoblinMarker",
	Chest = "ChestMarker",
	Exit = "ExitMarker",
}

function DungeonConfig.getObjective(roomName, state)
	state = state or {}

	if roomName == "StartRoom" then
		return "Explore a dungeon."
	end

	if roomName == "GoblinRoom" then
		if state.goblinDefeated then
			return "Goblin derrotado. Vá até a sala do tesouro."
		end
		return "Derrote o Goblin."
	end

	if roomName == "TreasureRoom" then
		if not state.goblinDefeated then
			return "Antes do baú, você precisa derrotar o Goblin."
		end
		if state.chestOpened then
			return "Baú aberto. Vá até a saída."
		end
		return "Abra o baú."
	end

	if roomName == "ExitRoom" then
		if state.runComplete then
			return "Vitória! Você escapou."
		end
		if state.goblinDefeated and state.chestOpened then
			return "A saída está livre. Use o prompt para escapar."
		end
		return "Ainda não é hora de sair."
	end

	return "Continue explorando."
end

return DungeonConfig