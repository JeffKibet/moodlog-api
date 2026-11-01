from datetime import datetime, timezone

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

from extensions import db, bcrypt

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)

    moods = db.relationship(
        "Mood", back_populates="user", cascade="all, delete-orphan"
    )

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates("username")
    def validate_username(self, key, value):
        if not value or not value.strip():
            raise ValueError("Username is required.")
        return value.strip()

    def to_dict(self):
        return {"id": self.id, "username": self.username}
class Mood(db.Model):
    __tablename__ = "moods"

    id = db.Column(db.Integer, primary_key=True)
    mood_score = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text)
    logged_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="moods")

    @validates("mood_score")
    def validate_mood_score(self, key, value):
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
            raise ValueError("Mood score must be a whole number from 1 to 5.")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "mood_score": self.mood_score,
            "note": self.note,
            "logged_at": self.logged_at.isoformat(),
            "user_id": self.user_id,
        }