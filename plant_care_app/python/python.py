from flask import Flask, jsonify, request

app = Flask(__name__)
API_KEY = "my_secret_key"

@app.route("/secure-data", methods=["GET"])
def secure_data():
    key = request.headers.get("Authorization")
    if key != f"Bearer {API_KEY}":
        return jsonify({"error": "Unauthorized"}), 401

    data = {"message": "Test Data"}
    return jsonify(data)

@app.route("/login", methods=["POST"])
def login():
    key = request.headers.get("Authorization")
    if key != f"Bearer {API_KEY}":
        return jsonify({"status": "fail", "message": "未授權"}), 401
    
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username == "flutter" and password == "123456":
        return jsonify({"status": "success", "message": "登入成功"})
    else:
        return jsonify({"status": "fail", "message": "帳號或密碼錯誤"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)