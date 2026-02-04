from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

commands = []
player_count = 0
banned_user_ids = set()
blacklisted_asset_ids = set()
blocked_hwids = set()
player_hwids = {}  # userid -> hwid
hwid_to_users = {} # hwid -> set(userids)

# Settings
settings = {
    "onjoin": True,
    "onlog": True,
    "banasync": True
}


@app.route("/")
def index():
    return "Flask server is running!"


@app.route("/send_command", methods=["POST"])
def send_command():
    data = request.json
    print(f"Get commands Discord bot: {data}")

    # If it's a ban command, add to banned_user_ids
    if data.get("command") == "ban":
        userid = data.get("userid")
        if userid:
            banned_user_ids.add(int(userid))
            print(f"✅ Banned UserId via send_command: {userid}")

    commands.append(data)
    return jsonify({"status": "OK"})

@app.route("/get_commands", methods=["GET"])
def get_commands():
    return jsonify(commands)


@app.route("/clear_commands", methods=["POST"])
def clear_commands():
    commands.clear()
    return jsonify({"status": "cleared"})


@app.route("/update_players", methods=["POST"])
def update_players():
    global player_count
    data = request.json
    player_count = data.get("count", 0)
    print(f"Players: {player_count}")
    return jsonify({"status": "updated"})


@app.route("/get_players")
def get_players():
    return jsonify({"count": player_count})


@app.route("/BanAsync", methods=["POST"])
def ban_async():
    data = request.json
    user_id = data.get("userid")
    if user_id:
        banned_user_ids.add(int(user_id))
        print(f"✅ Banned Async UserId: {user_id}")
        return jsonify({"status": "banned"})
    return jsonify({"error": "Missing userid"}), 400


@app.route("/check_webhooks", methods=["GET"])
def check_webhooks():
    # Placeholder for webhook tracking
    return jsonify({"webhooks": []})


@app.route("/deleteserverallwebhook", methods=["POST"])
def delete_all_webhooks():
    return jsonify({"status": "webhooks cleared"})


# === BAN SYSTEM ===


@app.route("/get_bans")
def get_bans():
    return jsonify([{"userid": str(uid), "username": "Unknown", "reason": "Banned via API", "executor": "System", "timestamp": "N/A"} for uid in banned_user_ids])


@app.route("/is_banned/<int:user_id>")
def is_banned(user_id):
    return jsonify({"banned": user_id in banned_user_ids})


@app.route("/ban", methods=["POST"])
def ban():
    data = request.json
    user_id = data.get("user_id")
    if user_id is not None:
        banned_user_ids.add(int(user_id))
        print(f"✅ Banned UserId: {user_id}")
        return jsonify({"status": "banned"})
    return jsonify({"error": "Missing user_id"}), 400


@app.route("/unban", methods=["POST"])
def unban():
    data = request.json
    user_id = data.get("user_id")
    if user_id is not None:
        banned_user_ids.discard(int(user_id))
        print(f"✅ Unbanned UserId: {user_id}")
        return jsonify({"status": "unbanned"})
    return jsonify({"error": "Missing user_id"}), 400


# === ASSET BLACKLIST ===

@app.route("/get_blacklist", methods=["GET"])
def get_blacklist():
    return jsonify({"assets": list(blacklisted_asset_ids)})

@app.route("/add_blacklist", methods=["POST"])
def add_blacklist():
    data = request.json
    asset_id = data.get("asset_id")
    if asset_id:
        blacklisted_asset_ids.add(str(asset_id))
        print(f"✅ Blacklisted AssetId: {asset_id}")
        return jsonify({"status": "blacklisted"})
    return jsonify({"error": "Missing asset_id"}), 400

@app.route("/remove_blacklist", methods=["POST"])
def remove_blacklist():
    data = request.json
    asset_id = data.get("asset_id")
    if asset_id:
        blacklisted_asset_ids.discard(str(asset_id))
        print(f"✅ Unblacklisted AssetId: {asset_id}")
        return jsonify({"status": "unblacklisted"})
    return jsonify({"error": "Missing asset_id"}), 400

@app.route("/clear_blacklist", methods=["POST"])
def clear_blacklist_api():
    blacklisted_asset_ids.clear()
    print("✅ Asset blacklist cleared")
    return jsonify({"status": "cleared"})

@app.route("/is_blacklisted/<string:asset_id>", methods=["GET"])
def is_blacklisted(asset_id):
    return jsonify({"blacklisted": asset_id in blacklisted_asset_ids})


# === HWID SYSTEM ===

@app.route("/hwid_block", methods=["POST"])
def hwid_block():
    data = request.json
    hwid = data.get("hwid")
    if hwid:
        blocked_hwids.add(str(hwid))
        print(f"✅ Blocked HWID: {hwid}")
        return jsonify({"status": "blocked"})
    return jsonify({"error": "Missing hwid"}), 400

@app.route("/hwid_unblock", methods=["POST"])
def hwid_unblock():
    data = request.json
    hwid = data.get("hwid")
    if hwid:
        blocked_hwids.discard(str(hwid))
        print(f"✅ Unblocked HWID: {hwid}")
        return jsonify({"status": "unblocked"})
    return jsonify({"error": "Missing hwid"}), 400

@app.route("/get_blocked_hwids", methods=["GET"])
def get_blocked_hwids():
    return jsonify({"hwids": list(blocked_hwids)})

@app.route("/update_hwid", methods=["POST"])
def update_hwid():
    data = request.json
    userid = data.get("userid")
    hwid = data.get("hwid")
    if userid and hwid:
        userid = str(userid)
        hwid = str(hwid)
        player_hwids[userid] = hwid
        if hwid not in hwid_to_users:
            hwid_to_users[hwid] = set()
        hwid_to_users[hwid].add(userid)
        return jsonify({"status": "updated"})
    return jsonify({"error": "Missing userid or hwid"}), 400

@app.route("/get_player_hwid/<string:userid>", methods=["GET"])
def get_player_hwid(userid):
    return jsonify({"hwid": player_hwids.get(str(userid))})

@app.route("/get_players_by_hwid/<string:hwid>", methods=["GET"])
def get_players_by_hwid(hwid):
    users = hwid_to_users.get(str(hwid), set())
    return jsonify({"users": list(users)})

@app.route("/check_hwid/<string:hwid>", methods=["GET"])
def check_hwid(hwid):
    return jsonify({"blocked": str(hwid) in blocked_hwids})


# === ANTI-CHEAT & UTILITY ===

@app.route("/report_anti", methods=["POST"])
def report_anti():
    data = request.json
    print(f"⚠️ Anti-Cheat Report: {data}")
    # Logic for auto-ban if needed
    if settings.get("banasync") and data.get("severity") == "high":
        userid = data.get("userid")
        if userid:
            banned_user_ids.add(int(userid))
            print(f"⚡ Auto-Banned via Anti-Cheat: {userid}")
    return jsonify({"status": "received"})

@app.route("/client_fix", methods=["POST"])
def client_fix():
    data = request.json
    fix_type = data.get("type")
    print(f"🛠️ Client Fix Requested: {fix_type}")
    commands.append({"command": "client_fix", "type": fix_type})
    return jsonify({"status": "sent"})

# === SETTINGS ===

@app.route("/get_settings", methods=["GET"])
def get_settings():
    return jsonify(settings)

@app.route("/update_settings", methods=["POST"])
def update_settings():
    data = request.json
    for key in settings:
        if key in data:
            settings[key] = data[key]
    return jsonify({"status": "updated", "settings": settings})


# === BANLIST JSON ===

@app.route("/bans/banlist.json")
def get_banlist_json():
    ban_list = []
    for uid in banned_user_ids:
        ban_list.append({
            "userid": str(uid),
            "username": "Unknown",
            "reason": "Banned via System",
            "executor": "System",
            "timestamp": datetime.now().timestamp()
        })
    return jsonify(ban_list)


def run():
    app.run(host="0.0.0.0", port=5000)