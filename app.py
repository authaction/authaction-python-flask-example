from dotenv import load_dotenv

load_dotenv()

from flask import Flask, g, jsonify

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
        "sub": g.current_user.get("sub"),
    })


if __name__ == "__main__":
    app.run(port=5000)
