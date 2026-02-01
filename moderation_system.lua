local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local DataStoreService = game:GetService("DataStoreService")

local API_URL = "https://a0077eee-c497-43f3-b189-c4c77d39fa4e-00-24uu76dd8yyu8.riker.replit.dev"

local function safeLog(message, level)
	level = level or "Kynx"
	local timestamp = os.date("%X")
	local logMessage = string.format("[%s] [%s] %s", timestamp, level, tostring(message))

	local success, err = pcall(function()
		if level == "WARN" then
			warn(logMessage)
		elseif level == "ERROR" then
			warn("[ERROR] " .. logMessage)
		else
			print(logMessage)
		end
	end)

	if not success then
		print("[FALLBACK LOG]", message)
	end
end

local BanStore, AllBansStore, PCBanStore, MuteStore

local function initializeDataStores()
	local success, err = pcall(function()
		BanStore = DataStoreService:GetDataStore("PlayerBans")
		AllBansStore = DataStoreService:GetDataStore("AllBansList")
		PCBanStore = DataStoreService:GetDataStore("PCPlayerBans")
		MuteStore = DataStoreService:GetDataStore("PlayerMutes")
		safeLog("DataStores successfully initialized")
		return true
	end)

	if not success then
		safeLog("Failed to initialize DataStores: " .. tostring(err), "ERROR")
		return false
	end
end

initializeDataStores()

local AnnouncementEvent, BroadcastEvent, ShutdownEvent

local function initializeEvents()
	local function getOrCreateEvent(name)
		local event = ReplicatedStorage:FindFirstChild(name)
		if not event then
			event = Instance.new("RemoteEvent")
			event.Name = name
			event.Parent = ReplicatedStorage
		end
		return event
	end

	local success, err = pcall(function()
		AnnouncementEvent = getOrCreateEvent("AnnouncementEvent")
		BroadcastEvent = getOrCreateEvent("BroadcastEvent")
		ShutdownEvent = getOrCreateEvent("ShutdownEvent")
		safeLog("RemoteEvents successfully initialized")
	end)

	if not success then
		safeLog("Failed to initialize RemoteEvents: " .. tostring(err), "ERROR")
	end
end

initializeEvents()

local function isOfficialBanAPIAvailable()
	local success = pcall(function()
		return Players.BanAsync ~= nil and Players.UnbanAsync ~= nil
	end)
	return success
end

function OfficialBanAsync(userId, durationSeconds, displayReason, privateReason, excludeAltAccounts)
	local success, errorMessage = pcall(function()
		Players:BanAsync({
			UserIds = {userId},
			ApplyToUniverse = true,
			Duration = durationSeconds,
			DisplayReason = displayReason,
			PrivateReason = privateReason,
			ExcludeAltAccounts = excludeAltAccounts or false,
		})
	end)

	if success then
		safeLog(string.format("Official BanAPI: Banned UserId %d for %d seconds | Reason: %s", 
			userId, durationSeconds, displayReason))
		return true
	else
		safeLog(string.format("Official BanAPI failed for UserId %d: %s", userId, tostring(errorMessage)), "ERROR")
		return false, errorMessage
	end
end

function OfficialUnbanAsync(userId)
	local success, errorMessage = pcall(function()
		Players:UnbanAsync({
			UserIds = {userId},
			ApplyToUniverse = true,
		})
	end)

	if success then
		safeLog("Official BanAPI: Unbanned UserId: " .. tostring(userId))
		return true
	else
		safeLog("Official BanAPI unban failed for UserId " .. tostring(userId) .. ": " .. tostring(errorMessage), "ERROR")
		return false, errorMessage
	end
end

local function safeDataStoreOperation(store, operation, ...)
	if not store then return nil, "DataStore not initialized" end
	local args = {...}
	local success, result = pcall(function()
		if operation == "get" then return store:GetAsync(table.unpack(args))
		elseif operation == "set" then return store:SetAsync(table.unpack(args))
		elseif operation == "remove" then return store:RemoveAsync(table.unpack(args))
		end
	end)
	if not success then safeLog("DataStore error: " .. tostring(result), "WARN") end
	return result, (not success and result or nil)
end

function MutePlayer(userId, duration, reason, executor)
	userId = tonumber(userId)
	local player = Players:GetPlayerByUserId(userId)
	local muteData = {
		endTime = os.time() + (duration * 60),
		reason = reason,
		executor = executor
	}
	safeDataStoreOperation(MuteStore, "set", tostring(userId), muteData)
	if player then
		player:SetAttribute("Muted", true)
		player:SetAttribute("MuteReason", reason)
		safeLog("Muted player " .. player.Name .. " for " .. duration .. " minutes")
	end
	return true
end

function UnmutePlayer(userId)
	userId = tonumber(userId)
	local player = Players:GetPlayerByUserId(userId)
	safeDataStoreOperation(MuteStore, "remove", tostring(userId))
	if player then
		player:SetAttribute("Muted", false)
		safeLog("Unmuted player " .. player.Name)
	end
	return true
end

-- Ban Check logic
local function checkBan(player)
	local userId = tostring(player.UserId)
	local banData = safeDataStoreOperation(BanStore, "get", userId)
	if banData then
		player:Kick("You are banned from this game. Reason: " .. (banData.reason or "No reason provided"))
		return true
	end
	
	local pcBanData = safeDataStoreOperation(PCBanStore, "get", userId)
	if pcBanData then
		player:Kick("Your device is banned from this game. Reason: " .. (pcBanData.reason or "No reason provided"))
		return true
	end
	
	return false
end

-- Polling Loop
spawn(function()
	while wait(5) do
		local success, result = pcall(function()
			local response = HttpService:GetAsync(API_URL .. "/get_commands")
			local commands = HttpService:JSONDecode(response)
			
			if #commands > 0 then
				HttpService:PostAsync(API_URL .. "/clear_commands", "{}")
				for _, data in ipairs(commands) do
					local cmd = data.command
					local userId = tonumber(data.userid)
					
					if cmd == "mute" then
						MutePlayer(userId, data.duration, data.reason, data.executor)
					elseif cmd == "umute" then
						UnmutePlayer(userId)
					elseif cmd == "kick" then
						local p = Players:GetPlayerByUserId(userId)
						if p then p:Kick(data.reason) end
					elseif cmd == "ban" then
						local banData = {reason = data.reason, duration = data.duration, executor = data.executor}
						safeDataStoreOperation(BanStore, "set", tostring(userId), banData)
						local p = Players:GetPlayerByUserId(userId)
						if p then p:Kick(data.reason) end
					elseif cmd == "unban" then
						safeDataStoreOperation(BanStore, "remove", tostring(userId))
					elseif cmd == "pcban" then
						local banData = {reason = data.reason, executor = data.executor}
						safeDataStoreOperation(PCBanStore, "set", tostring(userId), banData)
						local p = Players:GetPlayerByUserId(userId)
						if p then p:Kick(data.reason) end
					elseif cmd == "unpcban" then
						safeDataStoreOperation(PCBanStore, "remove", tostring(userId))
					elseif cmd == "announce" or cmd == "broadcast" then
						if AnnouncementEvent then AnnouncementEvent:FireAllClients(data.message) end
					elseif cmd == "shutdown" then
						for _, p in ipairs(Players:GetPlayers()) do
							p:Kick("Server is shutting down.")
						end
					end
				end
			end
		end)
		if not success then safeLog("Polling error: " .. tostring(result), "WARN") end
	end
end)

-- Asset Blacklist Check
local function checkAssetBlacklist()
	local success, result = pcall(function()
		local response = HttpService:GetAsync(API_URL .. "/get_blacklist")
		local blacklist = HttpService:JSONDecode(response)
		return blacklist
	end)
	return success and result or {}
end

Players.PlayerAdded:Connect(function(player)
	if checkBan(player) then return end
	
	local muteData = safeDataStoreOperation(MuteStore, "get", tostring(player.UserId))
	if muteData then
		if muteData.endTime > os.time() then
			player:SetAttribute("Muted", true)
			player:SetAttribute("MuteReason", muteData.reason)
		else
			safeDataStoreOperation(MuteStore, "remove", tostring(player.UserId))
		end
	end
end)
