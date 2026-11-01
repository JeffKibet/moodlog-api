from functools import wraps

from flask import request, session
from flask_restful import Resource

from extensions import db
from models import Mood


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return {"errors": ["Unauthorized. Please log in."]}, 401
        return fn(*args, **kwargs)
    return wrapper


def get_own_mood(mood_id):
    # Filtering by user_id means another user's record looks like it doesn't exist.
    return Mood.query.filter_by(id=mood_id, user_id=session["user_id"]).first()


class MoodList(Resource):
    method_decorators = [login_required]

    def get(self):
        page = max(request.args.get("page", 1, type=int), 1)
        per_page = max(request.args.get("per_page", 10, type=int), 1)
        pagination = (
            Mood.query.filter_by(user_id=session["user_id"])
            .order_by(Mood.logged_at.desc())
            .paginate(page=page, per_page=per_page, max_per_page=50, error_out=False)
        )
        return {
            "items": [m.to_dict() for m in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    def post(self):
        data = request.get_json() or {}
        try:
            mood = Mood(
                mood_score=data.get("mood_score"),
                note=data.get("note"),
                user_id=session["user_id"],
            )
        except ValueError as e:
            return {"errors": [str(e)]}, 422
        db.session.add(mood)
        db.session.commit()
        return mood.to_dict(), 201


class MoodDetail(Resource):
    method_decorators = [login_required]

    def patch(self, id):
        mood = get_own_mood(id)
        if not mood:
            return {"errors": ["Mood entry not found."]}, 404
        data = request.get_json() or {}
        try:
            if "mood_score" in data:
                mood.mood_score = data["mood_score"]
            if "note" in data:
                mood.note = data["note"]
        except ValueError as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422
        db.session.commit()
        return mood.to_dict(), 200

    def delete(self, id):
        mood = get_own_mood(id)
        if not mood:
            return {"errors": ["Mood entry not found."]}, 404
        db.session.delete(mood)
        db.session.commit()
        return "", 204