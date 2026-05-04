local ReplicatedStorage = game:GetService("ReplicatedStorage")

local hud = script.Parent
local roomLabel = hud:WaitForChild("RoomLabel")
local objectiveLabel = hud:WaitForChild("ObjectiveLabel")

local remotesFolder = ReplicatedStorage:WaitForChild("Remotes")
local roomChangedEvent = remotesFolder:WaitForChild("RoomChanged")
local objectiveChangedEvent = remotesFolder:WaitForChild("ObjectiveChanged")

roomLabel.Text = "Sala Inicial"
objectiveLabel.Text = "Explore a dungeon."

roomChangedEvent.OnClientEvent:Connect(function(roomName)
	roomLabel.Text = roomName
end)

objectiveChangedEvent.OnClientEvent:Connect(function(objectiveText)
	objectiveLabel.Text = objectiveText
end)