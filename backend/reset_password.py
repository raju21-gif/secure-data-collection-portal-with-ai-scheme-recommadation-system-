from database import users_collection
from auth import get_password_hash
import sys

def reset_user_password(email, new_password):
    user = users_collection.find_one({"email": email})
    if not user:
        print(f"User {email} not found!")
        return
    
    hashed_pw = get_password_hash(new_password)
    users_collection.update_one(
        {"email": email},
        {"$set": {"password": hashed_pw}}
    )
    print(f"SUCCESS: Password for {email} has been reset to: {new_password}")

if __name__ == "__main__":
    reset_user_password("rajapandi2105@gmail.com", "12345678")
