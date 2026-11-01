from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import User

class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        confirmation = data.get("password_confirmation") or ""

        errors = []
        if not username:
            errors.append("Username is required.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirmation:
            errors.append("Password and confirmation do not match.")
        if username and User.query.filter_by(username=username).first():
            errors.append("Username is already taken.")
        if errors:
            return {"errors": errors}, 422

        user = User(username=username)
        user.password_hash = password
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:  
            db.session.rollback()
            return {"errors": ["Username is already taken."]}, 422

        session["user_id"] = user.id
        return user.to_dict(), 201

class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = (data.get("username") or "").strip()
        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(data.get("password") or ""):
            session["user_id"] = user.id
            return user.to_dict(), 200
        return {"errors": ["Invalid username or password."]}, 401

class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        user = db.session.get(User, user_id) if user_id else None
        if user:
            return user.to_dict(), 200
        return {}, 401

class Logout(Resource):
    def delete(self):
        session.pop("user_id", None)
        return {}, 200