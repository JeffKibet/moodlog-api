import os
from flask import Flask
from flask_restful import Api
from extensions import db, migrate, bcrypt
from resources.auth import Signup, Login, CheckSession, Logout
from resources.moods import MoodList, MoodDetail


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    import models 

    api = Api(app)
    api.add_resource(Signup, "/signup")
    api.add_resource(Login, "/login")
    api.add_resource(CheckSession, "/check_session")
    api.add_resource(Logout, "/logout")
    api.add_resource(MoodList, "/moods")
    api.add_resource(MoodDetail, "/moods/<int:id>")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)