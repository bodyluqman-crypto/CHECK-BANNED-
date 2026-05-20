from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/checkbanned', methods=['GET'])
def check_banned():
    try:
        player_id = request.args.get('id')
        if not player_id:
            return jsonify({"error": "Player ID is required"}), 400

        # =======================
        # 1️⃣ Garena Ban Check
        # =======================
        garena_url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
            "Accept": "application/json, text/plain, */*",
            "referer": "https://ff.garena.com/en/support/"
        }

        g_res = requests.get(garena_url, headers=headers, timeout=10)
        ban_data = g_res.json() if g_res.status_code == 200 else {}

        is_banned = ban_data.get("data", {}).get("is_banned", 0)
        ban_period = ban_data.get("data", {}).get("period", 0)

        # =======================
        # 2️⃣ Profile / Region API
        # =======================
        region_url = f"https://nr-codex-apis.onrender.com/REGION-API/check?uid={player_id}"
        r_res = requests.get(region_url, timeout=10)
        region_data = r_res.json() if r_res.status_code == 200 else {}

        formatted = region_data.get("formatted_response", {})
        raw = region_data.get("raw_api_response", {})

        nickname = formatted.get("nickname")
        region = formatted.get("region")
        level = raw.get("basicInfo", {}).get("level")

        # =======================
        # 3️⃣ Final Output (ONLY REQUIRED)
        # =======================
        response = {
            "player_id": player_id,
            "nickname": nickname,
            "region": region,
            "level": level,
            "status": "BANNED" if is_banned else "NOT BANNED",
            "ban_period": ban_period if is_banned else 0
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/check_key', methods=['GET'])
def check_key():
    return jsonify({
        "status": "no_key_required",
        "message": "This API does not require an API key"
    })


# 🔥 Local + Vercel compatible
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port)