import Foundation

let source = URL(fileURLWithPath: CommandLine.arguments[1])
let data = try Data(contentsOf: source)
guard let document = try JSONSerialization.jsonObject(with: data) as? [String: Any],
      let domains = document["domains"] as? [String: [String: Any]] else {
    fatalError("Invalid app settings")
}

let processNames = [
    "com.bytieful.Gitfox-setapp": "Gitfox",
    "com.getcleanshot.app-setapp": "CleanShot X",
    "com.hieudinh.Compresto-setapp": "Compresto",
    "com.macpaw.CleanMyMac-setapp": "CleanMyMac",
    "com.nikolaeu.numi-setapp": "Numi",
    "com.proxyman.NSProxy-setapp": "Proxyman",
    "com.tinyapp.TablePlus-setapp": "TablePlus",
    "com.wiheads.paste-setapp": "Paste",
    "me.tdinh.devutils-setapp": "DevUtils",
    "pl.maketheweb.pixelsnap2-setapp": "PixelSnap",
]

func portable(_ value: Any) throws -> Any {
    if let string = value as? String {
        return string.replacingOccurrences(of: "__HOME__", with: NSHomeDirectory())
    }
    if let values = value as? [Any] {
        return try values.map(portable)
    }
    if let values = value as? [String: Any] {
        if let encoded = values["$jsonData"] {
            return try JSONSerialization.data(withJSONObject: encoded, options: [.sortedKeys])
        }
        return try values.mapValues(portable)
    }
    return value
}

func matches(_ current: Any, _ expected: Any) -> Bool {
    if let oldData = current as? Data,
       let newData = expected as? Data,
       let oldJSON = try? JSONSerialization.jsonObject(with: oldData),
       let newJSON = try? JSONSerialization.jsonObject(with: newData) {
        return NSDictionary(dictionary: ["value": oldJSON]).isEqual(to: ["value": newJSON])
    }
    return NSDictionary(dictionary: ["value": current]).isEqual(to: ["value": expected])
}

func isRunning(_ name: String) throws -> Bool {
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/pgrep")
    process.arguments = ["-x", name]
    process.standardOutput = Pipe()
    try process.run()
    process.waitUntilExit()
    return process.terminationStatus == 0
}

var applied = 0
for domain in domains.keys.sorted() {
    guard let defaults = UserDefaults(suiteName: domain),
          let preferences = domains[domain] else {
        fatalError("Cannot open \(domain) preferences")
    }
    var changes: [String: Any] = [:]
    for (key, value) in preferences {
        let expected = try portable(value)
        if let current = defaults.object(forKey: key), matches(current, expected) {
            continue
        }
        changes[key] = expected
    }
    if changes.isEmpty { continue }

    if let name = processNames[domain], try isRunning(name) {
        fputs("Quit \(name) before applying its settings, then rerun mise bootstrap.\n", stderr)
        exit(1)
    }
    for (key, value) in changes {
        defaults.set(value, forKey: key)
    }
    guard defaults.synchronize() else {
        fatalError("Could not save \(domain) settings")
    }
    applied += changes.count
}
print(applied == 0 ? "App settings already match" : "Applied \(applied) app setting(s)")
