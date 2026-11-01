from datetime import timezone
from random import choice, randint

from faker import Faker

from app import app
from extensions import db
from models import User, Mood

fake = Faker()

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "password123"
MOODS_PER_USER = 15 

def seed():
    with app.app_context():
        print("Clearing existing data...")
        Mood.query.delete()
        User.query.delete()
        db.session.commit()

        print("Creating users...")
        users = [User(username=DEMO_USERNAME)]
        for _ in range(3):
            users.append(User(username=fake.unique.user_name()))
        for user in users:
            user.password_hash = DEMO_PASSWORD  # hashed by the model's setter
        db.session.add_all(users)
        db.session.commit()

        print("Creating mood entries...")
        moods = []
        for user in users:
            for _ in range(MOODS_PER_USER):
                moods.append(
                    Mood(
                        mood_score=randint(1, 5),
                        note=choice([fake.sentence(), None]),
                        logged_at=fake.date_time_between(
                            start_date="-30d", end_date="now", tzinfo=timezone.utc
                        ),
                        user_id=user.id,
                    )
                )
        db.session.add_all(moods)
        db.session.commit()

        print(f"Seeded {len(users)} users and {len(moods)} mood entries.")
        print(f"Log in with username '{DEMO_USERNAME}' and password '{DEMO_PASSWORD}'.")


if __name__ == "__main__":
    seed()