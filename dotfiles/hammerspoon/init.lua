previousAppState = {
    currentBundleID = nil,
    lastTargetBundleID = nil,
    previousBundleID = nil,
    triggerCount = 0,
}

local ignoredBundleIDs = {
    ["com.brnbw.Tuna"] = true,
    ["com.getcleanshot.app-setapp"] = true,
    ["com.wiheads.paste-setapp"] = true,
    ["org.hammerspoon.Hammerspoon"] = true,
    ["pl.maketheweb.pixelsnap2-setapp"] = true,
}

local function rememberActivatedApp(app)
    if not app then
        return
    end

    local bundleID = app:bundleID()
    if not bundleID or ignoredBundleIDs[bundleID] then
        return
    end

    if bundleID ~= previousAppState.currentBundleID then
        previousAppState.previousBundleID = previousAppState.currentBundleID
        previousAppState.currentBundleID = bundleID
    end
end

rememberActivatedApp(hs.application.frontmostApplication())

appHistoryWatcher = hs.application.watcher.new(function(_, eventType, app)
    if eventType == hs.application.watcher.activated then
        rememberActivatedApp(app)
    elseif eventType == hs.application.watcher.terminated and app then
        local terminatedBundleID = app:bundleID()
        if terminatedBundleID == previousAppState.currentBundleID then
            previousAppState.currentBundleID = previousAppState.previousBundleID
            previousAppState.previousBundleID = nil
        elseif terminatedBundleID == previousAppState.previousBundleID then
            previousAppState.previousBundleID = nil
        end
    end
end)
appHistoryWatcher:start()

local function activatePreviousApp()
    local frontmostApp = hs.application.frontmostApplication()
    local frontmostBundleID = frontmostApp and frontmostApp:bundleID() or nil
    local frontmostIsIgnored = frontmostBundleID and ignoredBundleIDs[frontmostBundleID]
    local targetBundleID = frontmostIsIgnored
        and previousAppState.currentBundleID
        or previousAppState.previousBundleID

    if not targetBundleID then
        return
    end

    local targetApps = hs.application.applicationsForBundleID(targetBundleID)
    if not targetApps or #targetApps == 0 then
        if frontmostIsIgnored then
            previousAppState.currentBundleID = previousAppState.previousBundleID
        end
        previousAppState.previousBundleID = nil
        return
    end

    if not frontmostIsIgnored then
        previousAppState.previousBundleID = previousAppState.currentBundleID
        previousAppState.currentBundleID = targetBundleID
    end

    previousAppState.lastTargetBundleID = targetBundleID
    previousAppState.triggerCount = previousAppState.triggerCount + 1
    targetApps[1]:activate()
end

local backtickKeyCode = hs.keycodes.map["`"]

previousAppKeyTap = hs.eventtap.new({ hs.eventtap.event.types.keyDown }, function(event)
    if event:getKeyCode() ~= backtickKeyCode then
        return false
    end

    local flags = event:getFlags()
    if flags.cmd or flags.ctrl or flags.alt or flags.shift or flags.fn then
        return false
    end

    if event:getProperty(hs.eventtap.event.properties.keyboardEventAutorepeat) == 0 then
        activatePreviousApp()
    end

    return true
end)
previousAppKeyTap:start()
