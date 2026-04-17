# app/routes/auth.py
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required
from app.extensions import db, bcrypt
from app.models.user import User

bp = Blueprint("auth", __name__)

# REGISTER
@bp.post("/register")
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Campos obrigatórios"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email já existe"}), 400

    hash_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        username=username,
        email=email,
        password_hash=hash_pw
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Usuário criado"}), 201


# LOGIN
@bp.post("/login")
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    login_user(user)

    return jsonify({"message": "Login realizado com sucesso"})


# LOGOUT
@bp.post("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return jsonify({"message": "Logout realizado"})
