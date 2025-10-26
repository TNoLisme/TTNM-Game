import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL_SQLSERVER")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def main():
    # Create a session
    db = next(get_db())
    try:
        # Initialize repository
        from app.repository.users_repo import UsersRepository
        from app.models.users.user import User as UserModel
        from app.mapper.users_mapper import UsersMapper
        from app.domain.users.user import User

        repo = UsersRepository(db)

        # Get all users
        users = repo.get_all_users()
        if not users:
            print("No users found in the database.")
        else:
            print("List of all users:")
            for user in users:
                print(f"User ID: {user.user_id}")
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Role: {user.role}")
                print(f"Name: {user.name}")
                print(f"Password: {user.password}")
                print("---")

        # Get user by username (example: 'child1')
        sample_username = "child1"
        user = repo.get_by_username(sample_username)
        if user:
            print(f"\nUser found with username '{sample_username}':")
            print(f"User ID: {user.user_id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Name: {user.name}")
            print(f"Password: {user.password}")
        else:
            print(f"\nNo user found with username '{sample_username}'.")

        # Get user by username and password (example: 'child1' with 'user123')
        sample_username = "child1"
        sample_password = "user123"
        user = repo.get_by_username_and_password(sample_username, sample_password)
        if user:
            print(f"\nUser found with username '{sample_username}' and password '{sample_password}':")
            print(f"User ID: {user.user_id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Name: {user.name}")
            print(f"Password: {user.password}")
        else:
            print(f"\nNo user found with username '{sample_username}' and password '{sample_password}'.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()