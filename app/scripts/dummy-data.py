# populate_db.py
import random
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from faker import Faker

# Import your models
from app import models
from app.database.database import Base, engine

# Initialize Faker
fake = Faker()

# Create tables if they don't exist
print("Creating tables if they don't exist...")
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(bind=engine)

def create_dummy_data():
    session = SessionLocal()
    
    try:
        # Clear existing data (optional - be careful!)
        print("Clearing existing data...")
        session.query(models.Votes).delete()
        session.query(models.Post).delete()
        session.query(models.Users).delete()
        session.commit()
        print("Existing data cleared.")
        
        # Create 20 regular users
        print("Creating 20 regular users...")
        users = []
        for i in range(20):
            user = models.Users(
                email=fake.unique.email(),
                password=fake.password(length=12),
                created_at=datetime.now()
            )
            users.append(user)
        
        session.add_all(users)
        session.commit()
        print(f"Created {len(users)} regular users.")
        
        # Create the specific user: ahmed@burntbrains.com
        print("Creating specific user: ahmed@burntbrains.com...")
        
        # Check if user already exists
        existing_ahmed = session.query(models.Users).filter(
            models.Users.email == "ahmed@burntbrains.com"
        ).first()
        
        if existing_ahmed:
            print("User ahmed@burntbrains.com already exists. Using existing user.")
            ahmed = existing_ahmed
        else:
            ahmed = models.Users(
                email="ahmed@burntbrains.com",
                password="AhmedPassword123!",
                created_at=datetime.now()
            )
            session.add(ahmed)
            session.commit()
            print("Created ahmed@burntbrains.com user.")
        
        # Combine all users
        all_users = users + [ahmed]
        
        # Create posts for each user (2-5 posts per user)
        print("Creating posts for all users...")
        all_posts = []
        for user in all_users:
            num_posts = random.randint(2, 5)
            for j in range(num_posts):
                post = models.Post(
                    title=fake.sentence(nb_words=6).rstrip('.'),
                    content=fake.paragraph(nb_sentences=10),
                    published=random.choice([True, True, True, False]),  # 75% published
                    created_at=fake.date_time_this_year(),
                    user_id=user.id
                )
                all_posts.append(post)
        
        session.add_all(all_posts)
        session.commit()
        print(f"Created {len(all_posts)} total posts.")
        
        # Get ahmed's posts
        ahmed_posts = [post for post in all_posts if post.user_id == ahmed.id]
        
        if not ahmed_posts:
            # If ahmed has no posts, create one
            print("Ahmed has no posts. Creating a special post for him...")
            ahmed_special_post = models.Post(
                title="The Most Popular Post Ever!",
                content="This post has received over 1200 votes! Amazing content that everyone loves. Thank you all for your support!",
                published=True,
                created_at=datetime.now(),
                user_id=ahmed.id
            )
            session.add(ahmed_special_post)
            session.commit()
            target_post = ahmed_special_post
            all_posts.append(target_post)
        else:
            # Use the first post of ahmed as the target
            target_post = ahmed_posts[0]
        
        print(f"Selected target post ID: {target_post.id} (belongs to ahmed@burntbrains.com)")
        print(f"Post title: {target_post.title}")
        
        # Create 1200 votes for the target post
        print("\nCreating 1200 votes for ahmed's post...")
        
        # Exclude ahmed from voting on his own post
        potential_voters = [user for user in all_users if user.id != ahmed.id]
        
        # We need 1200 unique voters due to composite primary key
        if len(potential_voters) >= 1200:
            # We have enough unique users
            print(f"Using {len(potential_voters)} existing users for voting...")
            selected_voters = random.sample(potential_voters, 1200)
            votes = []
            for voter in selected_voters:
                vote = models.Votes(
                    voter_id=voter.id,
                    post_id=target_post.id
                )
                votes.append(vote)
        else:
            # Not enough users, create additional dummy users just for voting
            print(f"Only {len(potential_voters)} users available. Creating additional users for voting...")
            additional_voters_needed = 1200 - len(potential_voters)
            additional_voters = []
            
            for i in range(additional_voters_needed):
                dummy_user = models.Users(
                    email=f"voter_{i}_{fake.unique.email()}",
                    password=fake.password(length=12),
                    created_at=datetime.now()
                )
                additional_voters.append(dummy_user)
            
            session.add_all(additional_voters)
            session.commit()
            print(f"Created {additional_voters_needed} additional voting users.")
            
            # Combine all voters
            all_voters = potential_voters + additional_voters
            
            # Create votes for all 1200 voters
            votes = []
            for voter in all_voters:
                vote = models.Votes(
                    voter_id=voter.id,
                    post_id=target_post.id
                )
                votes.append(vote)
        
        # Add votes in batches to avoid memory issues
        print(f"Adding {len(votes)} votes in batches...")
        batch_size = 200
        for i in range(0, len(votes), batch_size):
            batch = votes[i:i+batch_size]
            session.add_all(batch)
            session.commit()
            print(f"  Added {len(batch)} votes... ({i+len(batch)}/{len(votes)})")
        
        print(f"Successfully added {len(votes)} votes to ahmed's post!")
        
        # Create random votes for other posts (so it looks natural)
        print("\nCreating additional random votes for other posts...")
        other_posts = [post for post in all_posts if post.id != target_post.id]
        
        random_votes = []
        votes_added = 0
        
        for post in other_posts:
            # Each post gets 0-50 random votes
            num_votes = random.randint(0, 50)
            # Get random voters (excluding the post owner)
            available_voters = [user for user in all_users if user.id != post.user_id]
            
            if available_voters and num_votes > 0:
                # Limit to available voters
                num_votes = min(num_votes, len(available_voters))
                voters_for_post = random.sample(available_voters, num_votes)
                
                for voter in voters_for_post:
                    # Check if vote already exists (to avoid duplicate primary key)
                    existing_vote = session.query(models.Votes).filter(
                        models.Votes.voter_id == voter.id,
                        models.Votes.post_id == post.id
                    ).first()
                    
                    if not existing_vote:
                        random_votes.append(models.Votes(
                            voter_id=voter.id,
                            post_id=post.id
                        ))
                        votes_added += 1
            
            # Add in batches to avoid memory issues
            if len(random_votes) >= 500:
                session.add_all(random_votes)
                session.commit()
                print(f"  Added batch of {len(random_votes)} random votes...")
                random_votes = []
        
        # Add remaining random votes
        if random_votes:
            session.add_all(random_votes)
            session.commit()
            print(f"  Added final batch of {len(random_votes)} random votes...")
        
        print(f"Added {votes_added} additional random votes to other posts.")
        
        # Print summary
        print("\n" + "="*60)
        print("DATABASE POPULATION COMPLETE!")
        print("="*60)
        
        # Get final counts
        total_users = session.query(models.Users).count()
        total_posts = session.query(models.Post).count()
        total_votes = session.query(models.Votes).count()
        
        print(f"Total Users: {total_users}")
        print(f"Total Posts: {total_posts}")
        print(f"Total Votes: {total_votes}")
        
        # Verify ahmed's post has 1200 votes
        actual_votes_count = session.query(models.Votes).filter(
            models.Votes.post_id == target_post.id
        ).count()
        
        print(f"\n✓ Votes on ahmed's post (ID: {target_post.id}): {actual_votes_count}")
        
        if actual_votes_count == 1200:
            print("✓ SUCCESS: ahmed@burntbrains.com has exactly 1200 votes on his post!")
        else:
            print(f"⚠ WARNING: Expected 1200 votes but got {actual_votes_count}")
        
        print(f"\n📊 Ahmed's post details:")
        print(f"   Title: {target_post.title}")
        print(f"   Content: {target_post.content[:150]}...")
        print(f"   Published: {target_post.published}")
        print(f"   Created at: {target_post.created_at}")
        
        # Show top 5 posts by vote count
        print("\n📈 Top 5 posts by vote count:")
        from sqlalchemy import func
        
        top_posts = session.query(
            models.Post.id,
            models.Post.title,
            func.count(models.Votes.post_id).label('vote_count')
        ).outerjoin(
            models.Votes, models.Post.id == models.Votes.post_id
        ).group_by(
            models.Post.id
        ).order_by(
            func.count(models.Votes.post_id).desc()
        ).limit(5).all()
        
        for i, post in enumerate(top_posts, 1):
            print(f"   {i}. Post {post.id}: '{post.title[:50]}' - {post.vote_count} votes")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print(f"Error type: {type(e).__name__}")
        session.rollback()
        raise
    finally:
        session.close()
        print("\nDatabase session closed.")

if __name__ == "__main__":
    print("Starting database population...")
    print(f"Database URL: {engine.url}")
    print("\nMake sure you have installed: pip install faker")
    print("-" * 60)
    
    try:
        create_dummy_data()
    except KeyboardInterrupt:
        print("\n\n⚠ Script interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Script failed: {e}")
        sys.exit(1)
        