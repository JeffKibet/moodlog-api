import os
from flask import Flask
from extensions import db, migrate, bcrypt
from flask_restful import Api
from resources.auth import Signup, Login, CheckSession, Logout

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
    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)