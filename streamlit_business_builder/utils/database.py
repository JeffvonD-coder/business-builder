from pymongo import MongoClient
import bcrypt
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        load_dotenv()  # Load environment variables
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client.business_builder
        self.users = self.db.users
        self.setup_indexes()

    def setup_indexes(self):
        """Create necessary indexes"""
        try:
            # Get list of existing indexes
            existing_indexes = self.users.list_indexes()
            existing_names = [idx['name'] for idx in existing_indexes]
            
            # Create case-insensitive index for username if it doesn't exist
            if "username_case_insensitive" not in existing_names:
                self.users.create_index(
                    [("username", 1)],
                    unique=True,
                    collation={'locale': 'en', 'strength': 2},
                    name="username_case_insensitive"
                )
            
            # Create email index if it doesn't exist
            if "email_unique" not in existing_names:
                self.users.create_index(
                    "email",
                    unique=True,
                    name="email_unique"
                )
        except Exception as e:
            logger.error(f"Error setting up indexes: {e}")

    def create_user(self, username, password, email, name, credits=5, is_admin=False):
        """Create a new user"""
        try:
            logger.info(f"Creating user: {username}")
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user = {
                "username": username,  # Keep original case for display
                "username_lower": username.lower(),  # Store lowercase for searching
                "password": hashed,
                "email": email,
                "name": name,
                "credits": credits,
                "is_admin": is_admin,
                "created_at": datetime.utcnow(),
                "last_login": None
            }
            self.users.insert_one(user)
            logger.info(f"User created successfully: {username}")
            return True
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return False

    def verify_user(self, username, password):
        """Verify user credentials"""
        try:
            logger.info(f"Verifying user: {username}")
            # Search case-insensitive
            user = self.users.find_one(
                {"username": {"$regex": f"^{username}$", "$options": "i"}},
                collation={'locale': 'en', 'strength': 2}
            )
            
            if not user:
                logger.warning(f"User not found: {username}")
                return None
                
            if not isinstance(user['password'], bytes):
                user['password'] = user['password'].encode('utf-8')
                
            if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                logger.info(f"User verified successfully: {username}")
                self.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"last_login": datetime.utcnow()}}
                )
                return user
            else:
                logger.warning(f"Invalid password for user: {username}")
                return None
        except Exception as e:
            logger.error(f"Error verifying user {username}: {e}")
            return None

    def get_user(self, username):
        """Get user by username"""
        try:
            return self.users.find_one(
                {"username": {"$regex": f"^{username}$", "$options": "i"}},
                collation={'locale': 'en', 'strength': 2}
            )
        except Exception as e:
            logger.error(f"Error getting user {username}: {e}")
            return None

    def update_credits(self, username, credits):
        """Update user credits"""
        try:
            self.users.update_one(
                {"username": {"$regex": f"^{username}$", "$options": "i"}},
                {"$set": {"credits": credits}},
                collation={'locale': 'en', 'strength': 2}
            )
            logger.info(f"Credits updated for user {username}: {credits}")
            return True
        except Exception as e:
            logger.error(f"Error updating credits for user {username}: {e}")
            return False

    def list_users(self):
        """List all users"""
        try:
            return list(self.users.find({}, {"password": 0}))
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    def delete_user(self, username):
        """Delete a user"""
        try:
            self.users.delete_one(
                {"username": {"$regex": f"^{username}$", "$options": "i"}},
                collation={'locale': 'en', 'strength': 2}
            )
            logger.info(f"User deleted: {username}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user {username}: {e}")
            return False

    def update_user(self, username, updates):
        """Update user details"""
        try:
            if "password" in updates:
                updates["password"] = bcrypt.hashpw(updates["password"].encode('utf-8'), bcrypt.gensalt())
            self.users.update_one(
                {"username": {"$regex": f"^{username}$", "$options": "i"}},
                {"$set": updates},
                collation={'locale': 'en', 'strength': 2}
            )
            logger.info(f"User updated: {username}")
            return True
        except Exception as e:
            logger.error(f"Error updating user {username}: {e}")
            return False

# Initialize database connection
def init_db():
    return Database() 