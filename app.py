from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request

from auth.jwt_validator import require_auth

app = Flask(__name__)


@app.get("/public")
def public_route():
    return jsonify({"message": "This is a public message!"})


@app.get("/protected")
@require_auth
def protected_route():
    return jsonify({
        "message": "This is a protected message!",
        "sub": request.current_payload.get("sub"),
    })


if __name__ == "__main__":
    app.run(port=5000)
