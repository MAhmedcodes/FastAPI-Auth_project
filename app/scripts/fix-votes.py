from sqlalchemy.orm import sessionmaker
from datetime import datetime
import random

from app import models
from app.database.database import engine

SessionLocal = sessionmaker(bind=engine)

def fix_ahmed_votes():

    session = SessionLocal()

    try:

        print("Finding Ahmed user...")

        ahmed = session.query(models.Users).filter(
            models.Users.email == "ahmed@burntbrains.com"
        ).first()

        if not ahmed:
            print("Ahmed user not found")
            return

        print(f"Ahmed found. ID: {ahmed.id}")

        # Get Ahmed posts
        posts = session.query(models.Post).filter(
            models.Post.user_id == ahmed.id
        ).all()

        if not posts:
            print("Ahmed has no posts")
            return

        target_post = posts[0]

        print(f"Target post ID: {target_post.id}")
        print(f"Title: {target_post.title}")

        # Delete existing votes
        print("Removing existing votes...")

        deleted = session.query(models.Votes).filter(
            models.Votes.post_id == target_post.id
        ).delete()

        session.commit()

        print(f"Removed {deleted} old votes")

        # Get all possible voters except Ahmed
        voters = session.query(models.Users).filter(
            models.Users.id != ahmed.id
        ).all()

        print(f"Available voters: {len(voters)}")

        # Create more voters if needed
        from faker import Faker
        fake = Faker()

        while len(voters) < 1200:

            user = models.Users(
                email=fake.unique.email(),
                password=fake.password(length=12),
                created_at=datetime.now()
            )

            session.add(user)
            session.flush()

            voters.append(user)

        session.commit()

        print(f"Total voters now: {len(voters)}")

        selected = random.sample(voters,1200)

        print("Creating 1200 votes...")

        votes = []

        for user in selected:

            votes.append(
                models.Votes(
                    voter_id=user.id,
                    post_id=target_post.id
                )
            )

        session.add_all(votes)
        session.commit()

        # Verify
        count = session.query(models.Votes).filter(
            models.Votes.post_id == target_post.id
        ).count()

        print("\nRESULT:")
        print(f"Votes on Ahmed post: {count}")

        if count == 1200:
            print("SUCCESS — Ahmed now has exactly 1200 votes")
        else:
            print("Something went wrong")

    except Exception as e:

        session.rollback()

        print("Error:",e)

    finally:

        session.close()

        print("Done")


if __name__ == "__main__":

    fix_ahmed_votes()
    